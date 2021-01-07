import requests
import logging
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Request

import labspace.utils as labut
from labspace.constants import ISSIGNED_URL, ALLOWEDOP_URL

# Get an instance of a logger
logger = logging.getLogger(__name__)

myConfig = labut.ConsentConfig('researcher')
myConfig.read_conf()

def update_request(request_obj):
    """
        Checks whether a request has been signed
        and what operations are allowed
    """
    # Perform API call
    cons_req = requests.get(f'{ISSIGNED_URL}/{request_obj.token}')
    
    # print(cons_req.json()['signed'])
    request_obj.not_replied()

    if cons_req.status_code == 200 and 'signed' in cons_req.json() and cons_req.json()['signed']:
        # request has been signed
        request_obj.replied()

        # Check what operations are allowed with an API call
        op_req = requests.get(f'{ALLOWEDOP_URL}/{request_obj.token}')

        if op_req.status_code == 200:
            op_results = op_req.json()
            # print(f'op_result: {op_results}')

            # Read and deserialise operations contained in the request
            operations_json = labut.SerializeOperations(myConfig)
            operations_json.unserialize(request_obj.operations)

            for op_result in op_results:
                # print(f"key: {op_result['key']}")
                operations_json.select_option_key(op_result['key'], op_result['chosen_option'])
            request_obj.operations = operations_json.serialize()
        else:
            logger.error(f'Call {ALLOWEDOP_URL}/{request_obj.token} gave {op_req.status_code} with {op_req.json()}')

    request_obj.save()

def gen_queryset(pk):
    """
        Return the requests, checking whether 
        they have been signed and what operations
        are allowed
    """
    request_set = None
    if pk == None:
        request_set = Request.objects.all()
    else:
        request_set = [Request.objects.get(pk=pk)]


    requests_view = []
    operations_json = labut.SerializeOperations(myConfig)

    for request_obj in request_set:
        update_request(request_obj)
        request_view = {}
        request_view['id'] = request_obj.id
        request_view['token'] = request_obj.token
        request_view['text'] = request_obj.text
        request_view['description'] = request_obj.description
        request_view['user_id'] = request_obj.user_id
        request_view['status'] = request_obj.status

        
        operations_json.unserialize(request_obj.operations)
        operations_view = []
        for operation in operations_json.operations:
            operation_view = {}
            operation_view['text'] = myConfig.get_operation_obj(operation['key']).text
            operation_view['chosen_option'] = operation['chosen_option']
            opt_obj = myConfig.get_option_obj(operation['chosen_option'])
            if not opt_obj == None:
                operation_view['chosen_option_text'] = opt_obj.text

            operations_view.append(operation_view)

        request_view['operations'] = operations_view
        # print(f"view operations {json.dumps(request_view['operations'])}")


        requests_view.append(request_view)
    
    if not pk == None:
        #  Return if just one request is needed
        return requests_view[0]

    operations_view = []
    for op_key in myConfig.operations.keys():
        operation_view = {}
        op_obj = myConfig.get_operation_obj(op_key)
        operation_view['key'] = op_obj.key
        operation_view['text'] = op_obj.text
        operations_view.append(operation_view)


    my_set = {}
    my_set['requests'] = requests_view
    my_set['operations'] = operations_view
    return my_set



def index(request):
    template_name = 'researcher_req/index.html'
    context = {'my_set' : gen_queryset(None)}
    return render(request, template_name, context)

def request(request, pk):
    template_name = 'researcher_req/request.html'
    context = {'request' : gen_queryset(pk)}
    return render(request, template_name, context)


def operation(request, key):
    template_name = 'researcher_req/operation.html'
    ope_obj = myConfig.get_operation_obj(key)
    opts_view = []
    for ope_key in ope_obj.options:
        opt_view = {}
        opt_obj = myConfig.get_option_obj(ope_key)
        opt_view['key'] = opt_obj.key
        opt_view['text'] = opt_obj.text
        opts_view.append(opt_view)

    ope_view = {}
    ope_view['options'] = opts_view
    ope_view['text'] = ope_obj.text
    ope_view['description'] = ope_obj.description

    context = {'operation' : ope_view}
    # print(f"operation html {ope_view}")
    return render(request, template_name, context)


def addrequest(request):
    """
        Generate new request
    """

    if request.method == 'POST':
        if 'operations' in request.POST:
            web_data= request.POST
            # print(f'request {web_data}')
            
            new_request = Request(text=web_data.get('text'), description=web_data.get(
                'description'), user_id=web_data.get('user_id'))
            new_request.save()
            
            # Add operations to request
            operations_ids = web_data.getlist('operations')
            operations_json = labut.SerializeOperations(myConfig)
            for id in operations_ids:
                operations_json.add_operation_key(id)
                # print(f'operation key: {ope_obj.key}')
                
            new_request.operations = operations_json.serialize()
            new_request.save()
            return HttpResponseRedirect(reverse('researcher_req:request', args=(new_request.id,)))
    return HttpResponseRedirect(reverse('researcher_req:index'))

def gentoken(request):
    if request.method == 'POST':
        if 'requestID' in request.POST:
            requestInst = get_object_or_404(Request, id=request.POST.get('requestID'))
            # print(f'request {request.POST}')
            # print(f'operation {operation for operation in requestInst.operations.all()}')
            operations_json = labut.SerializeOperations(myConfig)
            operations_json.unserialize(requestInst.operations)
            token = labut.gen_token(requestInst.user_id, operations_json.operations)
            requestInst.token = token
            requestInst.save()
            return HttpResponseRedirect(reverse('researcher_req:request', args=(requestInst.id,)))
    return HttpResponseRedirect(reverse('researcher_req:index'))
