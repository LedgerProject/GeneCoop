import json
from pyld import jsonld
import rdflib
from rdflib.parser import StringInputSource


doc = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "https://genecoop.waag.org/credentials/v1",
        {
            "gc_cred": "https://genecoop.waag.org/credentials/v1#",
            "gc_docs": "http://localhost:8000/docs/",
            "gc_ids": "http://localhost:8000/ids/",
            "gc_schema": "https://genecoop.waag.org/schema/v1#"
        }
    ],
    "credentialSubject": {
        "gc_cred:consents_to": [
            {
                "id": "gc_schema:exp_000",
                "name": "Array SNP request + Analysis and interpretation"
            },
            {
                "id": "gc_schema:exp_001",
                "name": "Copy Number Variation"
            },
            {
                "id": "gc_schema:exp_003",
                "name": "Population study. DNA data available for secondary use"
            }
        ],
        "gc_cred:prohibits": [
            {
                "id": "gc_schema:exp_002",
                "name": "SNP Variant detection (Biomarker or Pathogenic)"
            }
        ],
        "id": "http://localhost:8000/ids/pippo"
    },
    "given_to": {
        "id": "http://localhost:8000/ids/researcherA"
    },
    "id": "gc_docs:09e0178c3a",
    "issuanceDate": "2021-06-01T16:22:56.321Z",
    "issuer": {
        "id": "gc_ids:GeneCoop",
        "name": "GeneCoop Consent Service"
    },
    "name": "Consent for Eye Melanoma research",
    "proof": {
        "jws": "eyJhbGciOiJFUzI1NksiLCJiNjQiOnRydWUsImNyaXQiOiJiNjQifQ..s3vWQxGr2nyviG-9s9R4yRI0K1sSrLuR0YzOlOAqUv1G__j8gbGFitrnTFN89cERdVt6V40AEtCISJ2hGkpmrg",
        "proofPurpose": "authenticate",
        "type": "Zenroom",
        "verificationMethod": "BO7kDMVWprnCOgvAbsL3wBVMOd+2LrGTN90MkCJc1AaEe9df70Vm5Sc29M/y1mIc2D09tTvvhBQm6aB9U5k5Ew8="
    },
    "termsOfUse": [
        {
            "gc_cred:obligation": [
                {
                    "gc_cred:action": [
                        {
                            "id": "gc_cred:FetchLatestConsent"
                        }
                    ],
                    "gc_cred:assignee": {
                        "id": "gc_cred:AllVerifiers"
                    },
                    "gc_cred:assigner": {
                        "id": "gc_ids:GeneCoop"
                    },
                    "gc_cred:target": {
                        "id": "gc_docs:09e0178c3a"
                    }
                }
            ],
            "type": "gc_cred:IssuerPolicy"
        }
    ],
    "type": [
        "VerifiableCredential",
        "gc_cred:VerifiableConsent"
    ]
}
# compact a document according to a particular context
# see: https://json-ld.org/spec/latest/json-ld/#compacted-document-form
# compacted = jsonld.compact(doc, context)
# print(json.dumps(compacted, indent=2))
# compact using URLs
# jsonld.compact('http://example.org/doc', 'http://example.org/context')

def do_expansion(doc):
    # expand a document, removing its context
    # see: https://json-ld.org/spec/latest/json-ld/#expanded-document-form

    expanded = jsonld.expand(doc)
    print("EXPANDED")
    print(json.dumps(expanded, indent=2))

def do_urlexpansion(url):
    # # expand using URLs
    url_expanded = jsonld.expand(url)
    print("EXPANDED")
    print(json.dumps(url_expanded, indent=2))

def do_fileexpansion(file):
    with open(file) as f:
        fjson = json.loads(f.read())
        file_expanded = jsonld.expand(fjson)
    print("EXPANDED")
    print(json.dumps(file_expanded, indent=2))

def do_flatten(doc):
    # flatten a document
    # see: https://json-ld.org/spec/latest/json-ld/#flattened-document-form
    flattened = jsonld.flatten(doc)
    # all deep-level trees flattened to the top-level
    print("FLATTENED")
    print(json.dumps(flattened, indent=2))

def do_frame(doc, context):
    # frame a document
    # see: https://json-ld.org/spec/latest/json-ld-framing/#introduction
    framed = jsonld.frame(doc, context)
    # document transformed into a particular tree structure per the given frame
    print("FRAMED")
    print(json.dumps(framed, indent=2))

def do_normalize(doc):
    # normalize a document using the RDF Dataset Normalization Algorithm
    # (URDNA2015), see: https://json-ld.github.io/normalization/spec/
    normalized = jsonld.normalize(
        doc, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
    # normalized is a string that is a canonical representation of the document
    # that can be used for hashing, comparison, etc.
    
    # print("NORMALIZED")
    print(json.dumps(normalized, indent=2))
    return normalized


def do_query(query_body, msg):
    query_prefix = """
    PREFIX cred: <https://www.w3.org/2018/credentials#>
    PREFIX gc_cred: <https://genecoop.waag.org/credentials/v1#>
    PREFIX gc_docs: <http://localhost:8000/docs/>
    PREFIX gc_ids: <http://localhost:8000/ids/>
    PREFIX gc_schema: <https://genecoop.waag.org/schema/v1#>

    """
    query = query_prefix + query_body

    print(f'{msg}')
    for row in g.query(query):
        for l in row.__dict__['labels']:
            print(f'{l}: {row[l]}')


# test = '<https://genecoop.waag.org/schema/v1#exp_000> <http://www.w3.org/1999/02/22-rdf-syntax-ns#label> "Array SNP request + Analysis and interpretation" .'
test = do_normalize(doc)

g = rdflib.Graph()

source = StringInputSource(test.encode("utf8"))
g.load(source, format="nt")

query_body = """
    SELECT ?consent ?type ?name ?dna_donor ?researcher ?issuedate ?issuer ?issuername
    WHERE
    {
        ?consent    a                   ?type .
        FILTER (STRSTARTS(STR(?type),   "https://genecoop.waag.org/credentials/v1#"))
        ?consent    rdf:label           ?name;
                    cred:credentialSubject  ?dna_donor ;
                    gc_cred:given_to    ?researcher ;
                    cred:issuanceDate   ?issuedate ;
                    cred:issuer         ?issuer .
        ?issuer     rdf:label           ?issuername
    }

"""

do_query(query_body, 'Consent')


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

do_query(query_body, 'Allowed Experiments')

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

do_query(query_body, 'Not Allowed experiments')

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

do_query(query_body, 'Obligations')
