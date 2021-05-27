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
from researcher_app.models import User, Request

# from consent_server.constants import VERIFY_URL, DO_ENCODING

import consent_server.utils as labut

# Get an instance of a logger
logger = logging.getLogger(__name__)

myConfig = labut.read_conf('user')
mySerializedExperiments = labut.SerializeExperiments(myConfig)


def _gen_experimentset(experiment_str):
    # Generate a full description of the experiments
    # from the experiment string contained in the db 
    mySerializedExperiments.unserialize(experiment_str)
    experiment_entries = []
    for experiment in mySerializedExperiments.experiments:
        exp_obj = myConfig.get_experiment_obj(experiment['id'])
        option_entries = []
        for opt_id in myConfig.options:
            opt_obj = myConfig.get_option_obj(opt_id)
            opt_entry = {
                'id': opt_obj.id,
                'name': opt_obj.name,
            }
            option_entries.append(opt_entry)
        exp_entry = {
            'name': exp_obj.name,
            'id': exp_obj.id,
            'description': exp_obj.description,
            'procedures': [proc.description for proc in exp_obj.procedures],
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
    template_name = 'donor_app/token.html'
    return render(request, template_name)


def choose_view(request, token):
    logger.debug(f'Choose view request')
    if Consent.objects.filter(token=token).exists():
        consent = Consent.objects.get(token=token)
        if consent.is_signed():
            # The consent already exists and it is signed,
            # it cannot be modified without logging in
            logger.debug(f'Consent with token {token} already exists')
            return HttpResponseRedirect(reverse('donor_app:login'))

    template_name = 'donor_app/choose.html'
    my_request = get_object_or_404(Request, token=token)
    my_exps = {'experiments': _gen_experimentset(my_request.experiments)}
    context = {'my_exps': my_exps, 'my_request': my_request}
    return render(request, template_name, context)


def sign_view(request, token):
    logger.debug(f'Choose view request')

    template_name = 'donor_app/sign.html'

    my_request = get_object_or_404(Request, token=token)
    my_referent = {
        'first_name': my_request.researcher.user.first_name,
        'last_name': my_request.researcher.user.last_name,
        'institute': my_request.researcher.institute
    }

    my_consent = get_object_or_404(Consent, token=token)
    my_exps = {'experiments': _gen_experimentset(my_consent.experiments)}
    vc = labut.prepare_vc(token, my_request.researcher.user.username, my_exps['experiments'])
    my_vc = {'vc' : vc}
    context = {'my_exps': my_exps, 'my_consent': my_consent,
               'my_referent': my_referent, 'my_vc': my_vc}
    return render(request, template_name, context)


def login_view(request):
    logger.debug(f'Login view request')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('donor_app:index'))
    template_name = 'donor_app/login.html'
    # context = {'my_set' : _gen_queryset(None)}
    # logger.debug(f'Index view rendering: {json.dumps(context)}')
    context = {'challenge': labut.generate_random_challenge()}
    return render(request, template_name, context)

def logout_view(request):
    logger.debug(f'Logout view request')
    template_name = 'donor_app/logout.html'
    # breakpoint()
    if request.user.is_authenticated:
        logout(request)
        return render(request, template_name)
    return HttpResponseRedirect(reverse('donor_app:login'))

@login_required(login_url='donor_app:login')
def index_view(request):
    template_name = 'donor_app/index.html'
    context = {'my_set': _gen_queryset(None)}
    
    return render(request, template_name, context)


@login_required(login_url='donor_app:login')
def consent_view(request, pk):
    template_name = 'donor_app/consent.html'
    context = {'consent': _gen_queryset(pk, include_log=True)}
    return render(request, template_name, context)


def check_token(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            consent_req = get_object_or_404(Request, token=token)
            mySerializedExperiments.unserialize(consent_req.experiments)
            experiment_ids = [experiment['id'] for experiment in mySerializedExperiments.experiments]
            
            # Recreate the token to see that it matches
            match_token, _ = labut.gen_token(consent_req.name, consent_req.description,
                experiment_ids, consent_req.token_time)
            
            if not token == match_token:
                # token does not match, request is tampered with
                logger.warning(f'token match failed for token {token}')
            else:    
                public_key = consent_req.researcher.publickey
                token_signature = consent_req.token_signature
                if labut.verify_signature(public_key, token, token_signature):
                    logger.debug("Verification passed")

                    return HttpResponseRedirect(reverse('donor_app:choose', args=(token,)))
                else:
                    logger.warning(f'verification failed for token {token}')
        else:
            logger.warning(f'Call missing some parameters')

    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('donor_app:token'))


def gen_consent(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            consent_req = get_object_or_404(Request, token=token)

            mySerializedExperiments.unserialize(consent_req.experiments)

            for experiment in mySerializedExperiments.experiments:
                form_entry = f"option-{experiment['id']}"
                
                if form_entry in request.POST:
                    mySerializedExperiments.select_option_id(experiment['id'],
                                                             request.POST.get(form_entry))
                else:
                    mySerializedExperiments.reset_option_id(experiment['id'])

            new_consent = Consent(token=token,
                                    name=f'{consent_req.name}',
                                    description=f'{consent_req.description}')

            new_consent.init(mySerializedExperiments.serialize())
            new_consent.save()
            logger.debug("New consent created in unassigned state")
            return HttpResponseRedirect(reverse('donor_app:sign', args=(token,)))

    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('donor_app:token'))


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
            
            signed_vc = request.POST.get('signed_vc')
            public_key = request.POST.get('public_key')
            
            if labut.verify_signed_vc(public_key, signed_vc):
                logger.info("Signed VC Verification passed")
                myconsent.sign(signed_vc, public_key)
                myconsent.save()
                return HttpResponseRedirect(reverse('donor_app:index'))
            else:
                logger.error(f"Verification NOT passed, public_key {public_key}, token {token} and signed vc {signed_vc}")
    
    logger.warning(
        f'Default return from {inspect.currentframe().f_code.co_name}, something went wrong')
    return HttpResponseRedirect(reverse('donor_app:token'))


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
                return HttpResponseRedirect(reverse('donor_app:index'))
    logger.debug(f'Login failed')
    return HttpResponseRedirect(reverse('donor_app:login'))
