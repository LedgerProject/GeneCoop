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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .models import Consent
from researcher_req.models import User, Researcher, Request

# from labspace.constants import VERIFY_URL, DO_ENCODING

import labspace.utils as labut

# Get an instance of a logger
logger = logging.getLogger(__name__)

myConfig = labut.ConsentConfig('user')
myConfig.read_conf()
mySerializedExperiments = labut.SerializeExperiments(myConfig)


def _gen_experimentset(experiment_str):

    mySerializedExperiments.unserialize(experiment_str)
    experiment_entries = []
    for experiment in mySerializedExperiments.experiments:
        exp_obj = myConfig.get_experiment_obj(experiment['key'])
        option_entries = []
        for opt_key in exp_obj.options:
            opt_obj = myConfig.get_option_obj(opt_key)
            opt_entry = {
                'key': opt_obj.key,
                'name': opt_obj.name,
            }
            option_entries.append(opt_entry)
        exp_entry = {
            'name': exp_obj.name,
            'key': exp_obj.key,
            'description': exp_obj.description,
            'procedures': exp_obj.procedures,
            'required': exp_obj.required,
            'chosen_option': experiment['chosen_option'],
            'options': option_entries
        }
        experiment_entries.append(exp_entry)

    return experiment_entries


def _gen_queryset(pk, include_log=False):

    consent_set = None
    if pk == None:
        consent_set = Consent.objects.all()
    else:
        consent_set = [Consent.objects.get(pk=pk)]

    my_set = []

    for consent in consent_set:

        cons_entry = {
            'name': consent.name,
            'description': consent.description,
            'token': consent.token,
            'experiments': _gen_experimentset(consent.experiments)
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


def token_view(request):
    logger.debug(f'Token view request')
    template_name = 'genecoop/token.html'
    return render(request, template_name)


def choose_view(request, token):
    logger.debug(f'Choose view request')
    if Consent.objects.filter(token=token).exists():
        consent = Consent.objects.get(token=token)
        if consent.is_signed():
            # The consent already exists and it is signed,
            # it cannot be modified without logging in
            logger.debug(f'Consent with token {token} already exists')
            return HttpResponseRedirect(reverse('genecoop:login'))

    template_name = 'genecoop/choose.html'
    my_request = get_object_or_404(Request, token=token)
    my_exps = {'experiments': _gen_experimentset(my_request.experiments)}
    context = {'my_exps': my_exps, 'my_request': my_request}
    return render(request, template_name, context)


def sign_view(request, token):
    logger.debug(f'Choose view request')

    template_name = 'genecoop/sign.html'

    my_request = get_object_or_404(Request, token=token)
    my_referent = {
        'first_name': my_request.researcher.user.first_name,
        'last_name': my_request.researcher.user.last_name,
        'institute': my_request.researcher.institute
    }

    my_consent = get_object_or_404(Consent, token=token)
    my_exps = {'experiments': _gen_experimentset(my_consent.experiments)}
    context = {'my_exps': my_exps, 'my_consent': my_consent,
               'my_referent': my_referent}
    return render(request, template_name, context)


def login_view(request):
    logger.debug(f'Login view request')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('genecoop:index'))
    template_name = 'genecoop/login.html'
    # context = {'my_set' : _gen_queryset(None)}
    # logger.debug(f'Index view rendering: {json.dumps(context)}')
    context = {'challenge': labut.generate_random_challenge()}
    return render(request, template_name, context)

def logout_view(request):
    logger.debug(f'Logout view request')
    template_name = 'genecoop/logout.html'
    # breakpoint()
    if request.user.is_authenticated:
        logout(request)
        return render(request, template_name)
    return HttpResponseRedirect(reverse('genecoop:login'))

@login_required(login_url='genecoop:login')
def index_view(request):
    template_name = 'genecoop/index.html'
    context = {'my_set': _gen_queryset(None)}
    
    return render(request, template_name, context)


@login_required(login_url='genecoop:login')
def consent_view(request, pk):
    template_name = 'genecoop/consent.html'
    context = {'consent': _gen_queryset(pk, include_log=True)}
    return render(request, template_name, context)


def check_token(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            consent_req = get_object_or_404(Request, token=token)
            public_key = consent_req.researcher.publickey
            signature = consent_req.signature
            if labut.verify_signature(public_key, token, signature):
                logger.debug("Verification passed")

                return HttpResponseRedirect(reverse('genecoop:choose', args=(token,)))
            else:
                logger.warning(f'verification failed for token {token}')
        else:
            logger.warning(f'Call missing some parameters')

    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('genecoop:token'))


def gen_consent(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            consent_req = get_object_or_404(Request, token=token)

            mySerializedExperiments.unserialize(consent_req.experiments)

            for experiment in mySerializedExperiments.experiments:
                form_entry = f"option-{experiment['key']}"
                
                if form_entry in request.POST:
                    mySerializedExperiments.select_option_key(experiment['key'],
                                                             request.POST.get(form_entry))
                else:
                    mySerializedExperiments.reset_option_key(experiment['key'])

            new_consent = Consent(token=token,
                                    name=f'{consent_req.name}',
                                    description=f'{consent_req.description}')

            new_consent.init(mySerializedExperiments.serialize())
            new_consent.save()
            logger.debug("New consent created in unassigned state")
            return HttpResponseRedirect(reverse('genecoop:sign', args=(token,)))

    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('genecoop:token'))


def sign_consent(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        # print(f'request {request.POST}')

        if 'token' in request.POST:
            token = request.POST.get('token')
            myconsent = get_object_or_404(Consent, token=token)

            if not User.objects.filter(username=request.POST.get('public_key')).exists():
                user = User(username=request.POST.get('public_key'))
                user.save()
            
            signature = request.POST.get('signature')
            public_key = request.POST.get('public_key')
            hash = request.POST.get('hash')

            if labut.verify_signature(public_key, hash, signature):
                logger.debug("Verification passed")
                myconsent.sign(signature, public_key)
                myconsent.save()
                return HttpResponseRedirect(reverse('genecoop:index'))
            else:
                logger.error(f"Verification NOT passed, public_key {public_key}, hash {hash} and signature {signature}")
    
    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('genecoop:token'))


def check_login(request):
    """
        Check credentials and log user in
    """
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'user_id' in request.POST and 'challenge' in request.POST and 'response' in request.POST:
            public_key = request.POST['user_id']
            challenge = request.POST['challenge']
            response = request.POST['response']

            user = authenticate(request, is_researcher=False, username=public_key, challenge=challenge, response=response)
            
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('genecoop:index'))
    logger.debug(f'Login failed')
    return HttpResponseRedirect(reverse('genecoop:login'))


# def verify_consent(request):
#     logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
#     if request.method == 'POST':
#         if 'token' in request.POST and 'public_key' in request.POST:
#             token = request.POST.get('token')
#             public_key = request.POST.get('public_key')

#             requestInst = get_object_or_404(Request, token=token)

#             requestData = requestInst.token
#             signature = labut.get_signature(requestInst)

#             if DO_ENCODING:
#                 # Standard Base64 Encoding
#                 encodedBytes = base64.b64encode(requestData.encode("utf-8"))
#                 encodedStr = str(encodedBytes, "utf-8")
#             else:
#                 encodedStr = requestData

#             data = {
#                 "message": encodedStr,
#                 "message.signature": {
#                     "r": signature['r'],
#                     "s": signature['s'],
#                 },
#                 "Researcher": {
#                     "public_key": public_key
#                 }
#             }

#             # Verify signature
#             session = requests.Session()
#             verify_response = session.post(
#                 VERIFY_URL, json={"data": data})

#             logger.debug(
#                 f"Verification request: {labut.format_request(verify_response.request, 'utf8')}")

#             if verify_response.status_code == 200:
#                 logger.debug(f"Verification response: {verify_response.text}")
#                 zenroom_response = json.loads(verify_response.text)

#                 if 'output' in zenroom_response and zenroom_response['output'] == 'verification_passed':
#                     # verification is passed, create or retrieve consent
#                     logger.debug("Verification passed")

#                     user_id = requestInst.user_id

#                     try:
#                         new_consent = Consent.objects.get(token=token)
#                         logger.debug(
#                             f'Consent with token {token} already exists')
#                         return HttpResponseRedirect(reverse('genecoop:choose', args=(token,)))
#                     except Consent.DoesNotExist as error:
#                         # This is not an error, the consent does not yet exist
#                         pass

#                     new_consent = Consent(token=token,
#                                           text=f'{datetime.now()}',
#                                           description=f'Generated from token {token}',
#                                           user_id=user_id)

#                     mySerializedExperiments.unserialize(requestInst.experiments)
#                     new_consent.experiments = mySerializedExperiments.serialize()
#                     new_consent.save()
#                     logger.debug("New consent created")

#                     return HttpResponseRedirect(reverse('genecoop:choose', args=(token,)))
#                 else:
#                     logger.warning(
#                         f'verification failed, zenroom response: {zenroom_response}')
#             else:
#                 logger.error(
#                     f'Error from {VERIFY_URL}: {verify_response.status_code}')
#                 logger.error("Request that was sent:")
#                 logger.error(labut.format_request(
#                     verify_response.request, 'utf8'))
#         else:
#             logger.warning(f'Call missing some parameters')

#     logger.warning(
#         f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
#     return HttpResponseRedirect(reverse('genecoop:index'))
