from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Operation, Option, Request, read_table


read_table()

class IndexView(generic.ListView):
    template_name = 'researcher_req/index.html'
    context_object_name = 'my_set'

    def get_queryset(self):
        """Return the requests."""
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
            print(f'request {request.POST}')
            new_request = Request(name=request.POST.get('name'), description=request.POST.get(
                'description'), user_id=request.POST.get('user_id'))
            new_request.save()
            operations_ids = request.POST.getlist('operations')
            for id in operations_ids:
                operation = get_object_or_404(Operation, key=id)
                new_request.operations.add(Operation.objects.get(key=id))
            new_request.save()
            return HttpResponseRedirect(reverse('researcher_req:request', args=(new_request.id,)))
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
