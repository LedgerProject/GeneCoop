from datetime import datetime
import json
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
from django.urls import reverse
from django.views import generic
# from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view
from django.core.exceptions import MiddlewareNotUsed

from .models import Consent, SerializeOperations, read_conf

myConfig = read_conf()


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
    # print(f'sono io {token}')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if consent is not None:
            op_results = []
            for operation in consent.getOperations():
                op_result = {}
                op_result['key'] = operation['key']
                op_result['chosen_option'] = operation['chosen_option']
                op_results.append(op_result)
            # print(op_results)
            return Response(op_results)
    return Response({f'error': f'You need to provide a token'})
        

def gen_queryset(pk):
    my_set = []
    consent_set = None
    if pk == None:
        consent_set = Consent.objects.all()
    else:
        consent_set = [Consent.objects.get(pk=pk)]

    for consent in consent_set:
        operations_json = SerializeOperations()
        operations_json.unserializeOperations(consent.operations)
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

# class IndexView(generic.ListView):
#     model = Consent
#     template_name = 'genecoop/index.html'
#     context_object_name = 'my_set'

#     def get_queryset(self):
#         my_set = gen_queryset()
#         return my_set


# class ConsentView(generic.DetailView):
#     model = Consent
#     template_name = 'genecoop/consent.html'

# class SignConsentView(generic.DetailView):
#     model = Consent
#     template_name = 'genecoop/signconsent.html'
#     context_object_name = 'my_set'


#     def get_queryset(self):
#         my_set = gen_queryset()
#         return my_set

def sign(request, pk):
    template_name = 'genecoop/signconsent.html'
    context = {'my_set' : gen_queryset(pk)}
    return render(request, template_name, context)


def genconsent(request):
    if request.method == 'POST':
        if 'token' in request.POST:
            token = request.POST.get('token')
            mytokens = token.split('_')
            new_consent = None

            try:
                new_consent = Consent.objects.get(token=token)
            except Consent.DoesNotExist as error:
                # print(f'request {request.POST}')
                new_consent = Consent(token=request.POST.get('token'),
                                  text=f'{datetime.now()}', 
                                  description=f'Generated from token {request.POST.get("token")}', 
                                  user_id=mytokens[0])
                new_consent.save()

            operations_ids = mytokens[1:]
            operations_json = SerializeOperations()
            # print(f'Config: {myConfig}')
            for id in operations_ids:
                # print(f'id is {id}')
                operation = myConfig.get_operation(id)
                operations_json.addOperation(operation.key)
                for opt_key in operation.getOptions():
                    operations_json.addOption(operation.key, opt_key)
                    
            new_consent.operations = operations_json.serializeOperations()
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
            operations_json = SerializeOperations()
            operations_json.unserializeOperations(myconsent.operations)

            for operation in operations_json.operations:
                if f"option-{operation['key']}" in request.POST:
                    operations_json.selectOption(operation['key'], request.POST.get(
                        f"option-{ operation['key']}"))

            myconsent.operations = operations_json.serializeOperations()
            myconsent.sign()
            myconsent.save()
            return HttpResponseRedirect(reverse('genecoop:index'))
        return HttpResponseRedirect(reverse('genecoop:index'))

        # if 'token' in request.POST:
        #     mytokens = request.POST.get('token').split('_')

        #     # print(f'request {request.POST}')
        #     new_consent = Consent(
        #         name=f'{datetime.now()}', description=f'Generated from token {request.POST.get("token")}', user_id=mytokens[0])
        #     new_consent.save()
        #     operations_ids = mytokens[1:]
        #     for id in operations_ids:
        #         operation = get_object_or_404(Operation, key=id)
        #         # print(f'operation key: {operation.key}')
        #         # new_request.operations.add(Operation.objects.get(key=id))
        #         new_consent.operations.add(Operation.objects.get(key=id))
        #     new_consent.save()
        #     return HttpResponseRedirect(reverse('genecoop:sign', args=(new_consent.id,)))
    return HttpResponseRedirect(reverse('genecoop:index'))
