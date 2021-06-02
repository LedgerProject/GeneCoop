import requests
import logging
import inspect
import json

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.views import generic

from consent_server.constants import GENECOOP_URL

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

    context = {'request': {}}
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
