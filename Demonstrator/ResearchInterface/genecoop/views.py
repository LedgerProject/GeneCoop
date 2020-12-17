from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Operation, Option, Consent, read_table


read_table()

class IndexView(generic.ListView):
    model = Consent
    template_name = 'genecoop/index.html'
    # context_object_name = 'my_set'

class ConsentView(generic.DetailView):
    model = Consent
    template_name = 'genecoop/consent.html'


def genconsent(request):
    if request.method == 'POST':
        if 'token' in request.POST:
            mytokens = request.POST.get('token').split('_')

            # print(f'request {request.POST}')
            new_consent = Consent(name="", description="", user_id=mytokens[0])
            new_consent.save()
            operations_ids = mytokens[1:]
            for id in operations_ids:
                operation = get_object_or_404(Operation, key=id)
                # print(f'operation key: {operation.key}')
                # new_request.operations.add(Operation.objects.get(key=id))
                new_consent.operations.add(Operation.objects.get(key=id))
            new_consent.save()
            return HttpResponseRedirect(reverse('genecoop:sign', args=(new_consent.id,)))
    return HttpResponseRedirect(reverse('genecoop:index'))
