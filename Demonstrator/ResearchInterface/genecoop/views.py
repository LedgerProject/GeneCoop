from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
from django.urls import reverse
from django.views import generic
# from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view


from .models import Operation, Option, Consent, read_table


# read_table()

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
            return Response({f'Consent {token}':  consent.is_signed()})
    return Response({f'error': f'You need to provide a token'})
        


class IndexView(generic.ListView):
    model = Consent
    template_name = 'genecoop/index.html'

    def get_queryset(self):
        return Consent.objects.all()


# class ConsentView(generic.DetailView):
#     model = Consent
#     template_name = 'genecoop/consent.html'

class SignConsentView(generic.DetailView):
    model = Consent
    template_name = 'genecoop/signconsent.html'


def genconsent(request):
    if request.method == 'POST':
        if 'token' in request.POST:
            mytokens = request.POST.get('token').split('_')

            # print(f'request {request.POST}')
            new_consent = Consent(token=request.POST.get('token'),
                                  name=f'{datetime.now()}', 
                                  description=f'Generated from token {request.POST.get("token")}', 
                                  user_id=mytokens[0])
            new_consent.save()
            operations_ids = mytokens[1:]
            print(operations_ids)
            for id in operations_ids:
                operation = get_object_or_404(Operation, key=id)
                # print(f'operation key: {operation.key}')
                # new_request.operations.add(Operation.objects.get(key=id))
                new_consent.operations.add(Operation.objects.get(key=id))
            new_consent.save()
            return HttpResponseRedirect(reverse('genecoop:sign', args=(new_consent.token,)))
    return HttpResponseRedirect(reverse('genecoop:index'))


def signconsent(request):
    if request.method == 'POST':
        if 'consentID' in request.POST:
            # print(f'request {request.POST}')
            myconsent = get_object_or_404(
                Consent, token=request.POST.get('consentID'))
            for operation in myconsent.operations.all():
                if f'option-{ operation.key}' in request.POST:
                    # for option in operation.option_set.all():
                    operation.chosen_option = request.POST.get(
                        f'option-{ operation.key}')
                    operation.save()
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
