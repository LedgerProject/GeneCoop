from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.core.exceptions import MiddlewareNotUsed

from .models import Consent
import labspace.utils as labut

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
                    'key' : opt_obj.key,
                    'text' : opt_obj.text
                }
                option_entries.append(opt_entry)
            ope_entry = {
                'text' : ope_obj.text,
                'key' : ope_obj.key,
                'description' : ope_obj.description,
                'chosen_option' : operation['chosen_option'],
                'options' : option_entries
                }
            operation_entries.append(ope_entry)

        cons_entry = {
            'text' : consent.text,
            'token' : consent.token,
            'operations' : operation_entries
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
    context = {'my_set' : gen_queryset(None)}
    return render(request, template_name, context)

def consent(request, pk):
    template_name = 'genecoop/consent.html'
    context = {'consent' : gen_queryset(pk, include_log=True)}
    return render(request, template_name, context)

def sign(request, pk):
    template_name = 'genecoop/signconsent.html'
    context = {'my_set' : gen_queryset(pk)}
    return render(request, template_name, context)


def genconsent(request):
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            user_token, operations_token = labut.decode_token(token)
            new_consent = None

            try:
                new_consent = Consent.objects.get(token=token)
            except Consent.DoesNotExist as error:
                # print(f'request {request.POST}')
                new_consent = Consent(token=request.POST.get('token'),
                                  text=f'{datetime.now()}', 
                                  description=f'Generated from token {token}', 
                                  user_id=user_token)
                new_consent.save()

            mySerializedOperations.reset()
            for id in operations_token:
                # print(f'id is {id}')
                mySerializedOperations.add_operation_key(id)
                    
            new_consent.operations = mySerializedOperations.serialize()
            new_consent.save()
            return HttpResponseRedirect(reverse('genecoop:sign', args=(new_consent.token,)))
    return HttpResponseRedirect(reverse('genecoop:index'))


def signconsent(request):
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
