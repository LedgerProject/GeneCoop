import requests
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Operation, Option, Request, read_table


# read_table()

class IndexView(generic.ListView):
    host = 'http://localhost:8000'
    gc_issignedURL = f"{host}/api/is_signed"
    template_name = 'researcher_req/index.html'
    context_object_name = 'my_set'

    def get_queryset(self):
        """Return the requests."""
        for request in Request.objects.all():
            r = requests.get(f'{self.gc_issignedURL}/{request.token}')
            print(r)
            if r.status_code == 200:
                request.replied()
                request.save()
                
        my_set = {}
        my_set['requests'] = Request.objects.all()
        my_set['operations'] = Operation.objects.all()
        return my_set


class RequestView(generic.DetailView):
    model = Request
    template_name = 'researcher_req/request.html'


class OperationsView(generic.DetailView):
    model = Operation
    template_name = 'researcher_req/operation.html'

    def get_object(self, queryset=None):
        return Operation.objects.get(key=self.kwargs.get("key"))


def addrequest(request):
    if request.method == 'POST':
        if 'operations' in request.POST:
            # print(f'request {request.POST}')
            new_request = Request(name=request.POST.get('name'), description=request.POST.get(
                'description'), user_id=request.POST.get('user_id'))
            new_request.save()
            operations_ids = request.POST.getlist('operations')
            for id in operations_ids:
                operation = get_object_or_404(Operation, key=id)
                print(f'operation key: {operation.key}')
                # new_request.operations.add(Operation.objects.get(key=id))
                new_request.operations.add(Operation.objects.get(key=id))
            new_request.save()
            return HttpResponseRedirect(reverse('researcher_req:request', args=(new_request.id,)))
    return HttpResponseRedirect(reverse('researcher_req:index'))

def gentoken(request):
    if request.method == 'POST':
        if 'requestID' in request.POST:
            requestInst = get_object_or_404(Request, id=request.POST.get('requestID'))
            # print(f'request {request.POST}')
            # print(f'operation {operation for operation in requestInst.operations.all()}')
            opconcat = '_'.join([f'{operation.key}'.zfill(4) for operation in requestInst.operations.all()])
            requestInst.token = f'{requestInst.user_id}_{opconcat}'
            requestInst.save()
            return HttpResponseRedirect(reverse('researcher_req:request', args=(requestInst.id,)))
    return HttpResponseRedirect(reverse('researcher_req:index'))

    # try:
    #     selected_choice = question.choice_set.get(pk=request.POST['choice'])
    # except (KeyError, Choice.DoesNotExist):
    #     # Redisplay the question voting form.
    #     return render(request, 'polls/detail.html', {
    #         'question': question,
    #         'error_message': "You didn't select a choice.",
    #     })
    # else:
    #     selected_choice.votes += 1
    #     selected_choice.save()
    #     # Always return an HttpResponseRedirect after successfully dealing
    #     # with POST data. This prevents data from being posted twice if a
    #     # user hits the Back button.
    #     return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
