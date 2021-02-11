from datetime import datetime
import base64
import requests
import json
import logging
import inspect

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.core.exceptions import MiddlewareNotUsed

from .models import Consent
from researcher_req.models import Request

from labspace.constants import VERIFY_URL, DO_ENCODING

import labspace.utils as labut

# Get an instance of a logger
logger = logging.getLogger(__name__)

myConfig = labut.ConsentConfig('user')
myConfig.read_conf()
mySerializedOperations = labut.SerializeOperations(myConfig)


def gen_queryset(pk, include_log=False):

    consent_set = None
    if pk == None:
        consent_set = Consent.objects.all()
    else:
        consent_set = [Consent.objects.get(pk=pk)]

    my_set = []

    for consent in consent_set:

        mySerializedOperations.unserialize(consent.operations)
        operation_entries = []
        for operation in mySerializedOperations.operations:
            ope_obj = myConfig.get_operation_obj(operation['key'])
            option_entries = []
            for opt_key in ope_obj.options:
                opt_obj = myConfig.get_option_obj(opt_key)
                opt_entry = {
                    'key': opt_obj.key,
                    'text': opt_obj.text
                }
                option_entries.append(opt_entry)
            ope_entry = {
                'text': ope_obj.text,
                'key': ope_obj.key,
                'description': ope_obj.description,
                'chosen_option': operation['chosen_option'],
                'options': option_entries
            }
            operation_entries.append(ope_entry)

        cons_entry = {
            'text': consent.text,
            'token': consent.token,
            'operations': operation_entries
        }
        if include_log:
            log_entries = []
            for log_obj in consent.consentlogger_set.all().order_by('-request_received'):
                log_entry = {}
                log_entry['time'] = log_obj.request_received
                log_entry['type'] = log_obj.type
                log_entry['message'] = log_obj.message
                log_entries.append(log_entry)
            cons_entry['logs'] = log_entries

        my_set.append(cons_entry)

    # print(f"My Set {my_set}")

    if pk == None:
        return my_set
    else:
        return my_set[0]


def index(request):
    template_name = 'genecoop/index.html'
    context = {'my_set': gen_queryset(None)}
    return render(request, template_name, context)


def consent(request, pk):
    template_name = 'genecoop/consent.html'
    context = {'consent': gen_queryset(pk, include_log=True)}
    return render(request, template_name, context)


def sign(request, pk):
    template_name = 'genecoop/signconsent.html'
    my_set = gen_queryset(pk)
    my_request = get_object_or_404(Request, token=pk)
    context = {'my_set': my_set, 'my_request': my_request}
    return render(request, template_name, context)


def verify_consent(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'token' in request.POST and 'public_key' in request.POST:
            token = request.POST.get('token')
            public_key = request.POST.get('public_key')

            requestInst = get_object_or_404(Request, token=token)

            requestData = labut.request_to_sign(requestInst)
            signature = labut.get_signature(requestInst)

            if DO_ENCODING:
                # Standard Base64 Encoding
                encodedBytes = base64.b64encode(requestData.encode("utf-8"))
                encodedStr = str(encodedBytes, "utf-8")
            else:
                encodedStr = requestData

            data = {
                "message": encodedStr,
                "message.signature": {
                    "r": signature['r'],
                    "s": signature['s'],
                },
                "Researcher": {
                    "public_key": public_key
                }
            }

            # Verify signature
            session = requests.Session()
            verify_response = session.post(
                VERIFY_URL, json={"data": data})

            logger.debug(f"Verification request: {labut.format_request(verify_response.request, 'utf8')}")

            if verify_response.status_code == 200:
                logger.debug(f"Verification response: {verify_response.text}")
                zenroom_response = json.loads(verify_response.text)

                if 'output' in zenroom_response and zenroom_response['output'] == 'verification_passed':
                    # verification is passed, create or retrieve consent
                    logger.debug("Verification passed")

                    user_id = requestInst.user_id

                    try:
                        new_consent = Consent.objects.get(token=token)
                        logger.debug(f'Consent with token {token} already exists')
                        return HttpResponseRedirect(reverse('genecoop:sign', args=(token,)))
                    except Consent.DoesNotExist as error:
                        # This is not an error, the consent does not yet exist
                        pass
            
                    new_consent = Consent(token=token,
                              text=f'{datetime.now()}',
                              description=f'Generated from token {token}',
                              user_id=user_id)
                    
                    mySerializedOperations.unserialize(requestInst.operations)
                    new_consent.operations = mySerializedOperations.serialize()
                    new_consent.save()
                    logger.debug("New consent created")

                    return HttpResponseRedirect(reverse('genecoop:sign', args=(token,)))
                else:
                    logger.warning(f'verification failed, zenroom response: {zenroom_response}')        
            else:
                logger.error(
                    f'Error from {VERIFY_URL}: {verify_response.status_code}')
                logger.error("Request that was sent:")
                logger.error(labut.format_request(verify_response.request, 'utf8'))
        else:
            logger.warning(f'Call missing some parameters')

    logger.warning(f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('genecoop:index'))


def signconsent(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        # print(f'request {request.POST}')

        if 'consentID' in request.POST:
            token = request.POST.get('consentID')

            myconsent = get_object_or_404(
                Consent, token=token)

            # print(f'consent op {myconsent.operations}')

            mySerializedOperations.unserialize(myconsent.operations)

            for operation in mySerializedOperations.operations:
                if f"option-{operation['key']}" in request.POST:
                    mySerializedOperations.select_option_key(operation['key'], request.POST.get(
                        f"option-{ operation['key']}"))

            myconsent.operations = mySerializedOperations.serialize()
            myconsent.sign()
            myconsent.save()
            return HttpResponseRedirect(reverse('genecoop:index'))
        return HttpResponseRedirect(reverse('genecoop:index'))

    return HttpResponseRedirect(reverse('genecoop:index'))
