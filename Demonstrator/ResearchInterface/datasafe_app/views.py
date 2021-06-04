import requests
import logging
import inspect
import json
from pyld import jsonld
import rdflib
from rdflib.parser import StringInputSource


from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.views import generic

from consent_server.constants import GENECOOP_URL, GC_CRED, GENECOOP_URL, GC_SCHEMA

import consent_server.utils as labut

# Get an instance of a logger
logger = logging.getLogger(__name__)
# print(f'Logger {__name__}')

def _retrieve_vc(token):
    vc = labut.get_vc(token)
    public_key = labut.get_publickey(vc['credentialSubject']['id'])
    if not labut.verify_signed_vc(public_key, vc):
        return None
    return vc

def _do_normalize(doc):
    # normalize a document using the RDF Dataset Normalization Algorithm
    # (URDNA2015), see: https://json-ld.github.io/normalization/spec/
    normalized = jsonld.normalize(
        doc, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
    
    # print("NORMALIZED")
    # print(json.dumps(normalized, indent=2))
    return normalized

def _gen_pageset(vc):

    norm_vc = _do_normalize(vc)

    SPARQL_PREFIX = f"""
    PREFIX cred: <https://www.w3.org/2018/credentials#>
    PREFIX gc_cred: <{GC_CRED}>
    PREFIX gc_docs: <{GENECOOP_URL}/docs/>
    PREFIX gc_ids: <{GENECOOP_URL}/ids/>
    PREFIX gc_schema: <{GC_SCHEMA}>

    """
    # Initialize the RDF graph
    g = rdflib.Graph()
    if isinstance(norm_vc, dict):
        norm_vc = json.dumps(norm_vc)

    logger.debug(f'VC is {vc}')
    logger.debug(f'Normalized VC is {norm_vc}')

    # Normalize the VC to N-triple format and load it in the graph
    source = StringInputSource(norm_vc.encode("utf8"))
    g.load(source, format="nt")

    # inizialize context to return
    context = {}
    context['orig_vc'] = vc
    context['norm_vc'] = norm_vc

    # Perform SPARQL queries against the graph

    query_body = f'''
    SELECT ?consent ?type ?name ?dna_donor ?researcher ?issuedate ?issuer ?issuername
    WHERE
    {{
        ?consent    a                   ?type .
        FILTER (STRSTARTS(STR(?type),   "{GC_CRED}"))
        ?consent    rdf:label           ?name;
                    cred:credentialSubject  ?dna_donor ;
                    gc_cred:given_to    ?researcher ;
                    cred:issuanceDate   ?issuedate ;
                    cred:issuer         ?issuer .
        ?issuer     rdf:label           ?issuername
    }}
    '''

    query = SPARQL_PREFIX + query_body

    logger.debug(f'Consent')
    
    for row in g.query(query):
        context['id'] = row['consent']
        context['name'] = row['name']
        context['given_by'] = row['dna_donor']
        context['given_to'] = row['researcher']
        context['issuedate'] = row['issuedate']
        context['issuer'] = row['issuer']
        context['issuername'] = row['issuername']
        logger.debug(f"Consent {json.dumps(context)}")


    query_body = """
    SELECT ?experiment ?experiment_name

    WHERE
    {
        ?consent    a          gc_cred:VerifiableConsent .
        ?consent    cred:credentialSubject  ?dna_donor .
        ?dna_donor  gc_cred:consents_to  ?experiment .
        ?experiment rdf:label ?experiment_name
    }
    """

    query = SPARQL_PREFIX + query_body

    context['allowed_exps'] = []
    logger.debug(f'Allowed experiments')

    for row in g.query(query):
        exp = {}
        exp['id'] = row['experiment']
        exp['name'] = row['experiment_name']
        logger.debug(f"Experiment id {exp['id']} and name {exp['name']}")
        context['allowed_exps'].append(exp)



    query_body = """
    SELECT ?experiment ?experiment_name

    WHERE
    {
        ?consent    a          gc_cred:VerifiableConsent .
        ?consent    cred:credentialSubject  ?dna_donor .
        ?dna_donor  gc_cred:prohibits  ?experiment .
        ?experiment rdf:label ?experiment_name
    }
    """

    logger.debug(f'Not Allowed experiments')
    query = SPARQL_PREFIX + query_body

    context['non_allowed_exps'] = []

    for row in g.query(query):
        exp = {}
        exp['id'] = row['experiment']
        exp['name'] = row['experiment_name']
        logger.debug(f"Experiment id {exp['id']} and name {exp['name']}")
        context['non_allowed_exps'].append(exp)

    query_body = """
    SELECT ?action ?parties

    WHERE
    {
        ?consent    a          gc_cred:VerifiableConsent .
        ?consent    cred:termsOfUse  ?terms_of_use .
        ?terms_of_use a         gc_cred:IssuerPolicy .
        ?terms_of_use  gc_cred:obligation  ?obligation .
        ?obligation gc_cred:action ?action .
        ?obligation gc_cred:assignee ?parties
    }
    """

    logger.debug(f'Obligations')
    query = SPARQL_PREFIX + query_body

    context['obligations'] = []

    for row in g.query(query):
        action = {}
        action['action'] = row['action']
        action['parties'] = row['parties']
        logger.debug(f"Action id {action['action']} for parties {action['parties']}")
        context['obligations'].append(action)

    return context

def index_view(request):
    logger.debug(f'Index view request')
    template_name = 'datasafe_app/index.html'
    context = {'my_set': {}}
    logger.debug(f'Index view rendering: {json.dumps(context)}')
    return render(request, template_name, context)

def vc_view(request, token):
    logger.debug(f'VC view request')
    template_name = 'datasafe_app/vc.html'
    vc = _retrieve_vc(token)
    if vc == None:
        err_msg = f'VC: {token} did not pass verification'
        logger.error(err_msg)
        return HttpResponseBadRequest(err_msg)
    
    parsed_vc = _gen_pageset(vc)

    context = {'vc': parsed_vc}

    logger.debug(f'VC view rendering: {json.dumps(context)}')
    return render(request, template_name, context)


def retrieve_vc(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'vc_url' in request.POST:
            vc_url = request.POST.get('vc_url')
            if vc_url.startswith(f"{GENECOOP_URL}/docs/"):
                vc_url = vc_url[len(f"{GENECOOP_URL}/docs/"):]
    
            logger.debug(f'Return token {vc_url} for vc')
            return HttpResponseRedirect(reverse('datasafe_app:vc', args=(vc_url,)))
    
    logger.debug(f'Returning without action')
    return HttpResponseRedirect(reverse('datasafe_app:index'))
