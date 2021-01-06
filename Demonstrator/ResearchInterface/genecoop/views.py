from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
from django.urls import reverse
from django.views import generic
from rest_framework import permissions
from rest_framework.decorators import api_view
from django.core.exceptions import MiddlewareNotUsed

from .models import Consent
import labspace.utils as labut

myConfig = labut.ConsentConfig('user')
myConfig.read_conf()

# class ReadConfMiddleware:
#     def __init__(self, get_response):
#         print("in the middleware")
#         self.get_response = get_response
#         # if myConfig == None:
#         #     read_conf()
#         #     print(f"Read conf, {type(myConfig)}")
#         # else:
#         #     raise MiddlewareNotUsed('Config already read')
#         # One-time configuration and initialization.

#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.

#         response = self.get_response(request)

#         # Code to be executed for each request/response after
#         # the view is called.

#         return response

@api_view((['GET']))
def ping(request):
    return Response({f'message': 'Hello'})

@api_view((['GET']))
def is_signed(request, token):
    # print(f'sono io {token}')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if consent is not None:
            return Response({"token" : token,
                              "signed" : consent.is_signed()})
    return Response({f'error': f'You need to provide a token'})
        
@api_view((['GET']))
def allowed_operations(request, token):
    # print(f'token {token}')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if consent is not None:
            op_results = []
            operations_json = labut.SerializeOperations(myConfig)
            operations_json.unserialize(consent.operations)
            for operation in operations_json.operations:
                op_result = {}
                op_result['key'] = operation['key']
                op_result['chosen_option'] = operation['chosen_option']
                op_results.append(op_result)
            # print(op_results)
            return Response(op_results)
    return Response({f'error': f'You need to provide a token'})
        

def gen_queryset(pk):
    
    consent_set = None
    if pk == None:
        consent_set = Consent.objects.all()
    else:
        consent_set = [Consent.objects.get(pk=pk)]

    my_set = []
    operations_json = labut.SerializeOperations(myConfig)
    for consent in consent_set:
        
        operations_json.unserialize(consent.operations)
        operation_entries = []
        for operation in operations_json.operations:
            ope_obj = myConfig.get_operation(operation['key'])
            option_entries = []
            for opt_key in ope_obj.options:
                opt_obj = myConfig.get_option(opt_key)
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
            'operations' : operation_entries}
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
                                  description=f'Generated from token {request.POST.get("token")}', 
                                  user_id=user_token)
                new_consent.save()

            operations_json = labut.SerializeOperations(myConfig)
            # print(f'Config: {myConfig}')
            for id in operations_token:
                # print(f'id is {id}')
                operations_json.add_operation(id)
                    
            new_consent.operations = operations_json.serialize()
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
            operations_json = labut.SerializeOperations(myConfig)
            operations_json.unserialize(myconsent.operations)

            for operation in operations_json.operations:
                if f"option-{operation['key']}" in request.POST:
                    operations_json.select_option(operation['key'], request.POST.get(
                        f"option-{ operation['key']}"))

            myconsent.operations = operations_json.serialize()
            myconsent.sign()
            myconsent.save()
            return HttpResponseRedirect(reverse('genecoop:index'))
        return HttpResponseRedirect(reverse('genecoop:index'))

    return HttpResponseRedirect(reverse('genecoop:index'))
