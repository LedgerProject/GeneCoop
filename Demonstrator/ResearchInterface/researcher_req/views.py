import requests
import logging
import inspect
import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required


from .models import Request, Researcher

import labspace.utils as labut
from labspace.constants import ISSIGNED_URL, ALLOWEDOP_URL, LOGOP_URL

# Get an instance of a logger
logger = logging.getLogger(__name__)
# print(f'Logger {__name__}')

myConfig = labut.ConsentConfig('researcher')
myConfig.read_conf()
mySerializedOperations = labut.SerializeOperations(myConfig)


def _update_request(request_obj):
    """
        Checks whether a request has been signed
        and what operations are allowed
    """
    if request_obj.token == None or request_obj.token == "":
        logger.debug(f'Request {request_obj.id} does not have a token yet')
        return

    # Perform API call
    logger.debug(f'Perform request {ISSIGNED_URL}/{request_obj.token}')
    cons_req = requests.get(f'{ISSIGNED_URL}/{request_obj.token}')

    # print(cons_req.json()['signed'])
    request_obj.not_replied()

    if cons_req.status_code == 200:
        if 'signed' in cons_req.json() and cons_req.json()['signed']:
            # request has been signed
            logger.debug(f'Request result: {cons_req.json()}')
            request_obj.replied()

            # Check what operations are allowed with an API call
            logger.debug(
                f'Perform request {ALLOWEDOP_URL}/{request_obj.token}')
            op_req = requests.get(f'{ALLOWEDOP_URL}/{request_obj.token}')

            if op_req.status_code == 200:
                logger.debug(f'Request result: {op_req.json()}')
                op_results = op_req.json()
                # print(f'op_result: {op_results}')

                # Read and deserialise operations contained in the request
                logger.debug(f'Start deserialize operations')

                mySerializedOperations.unserialize(request_obj.operations)
                logger.debug(
                    f'Deserialize operations: {request_obj.operations}')

                for op_result in op_results:
                    # print(f"key: {op_result['key']}")
                    mySerializedOperations.select_option_key(
                        op_result['key'], op_result['chosen_option'])

                request_obj.operations = mySerializedOperations.serialize()
                logger.debug(f'Serialize operations: {request_obj.operations}')
            else:
                logger.error(
                    f'Call {ALLOWEDOP_URL}/{request_obj.token} gave {op_req.status_code} with {op_req.text}')
    else:
        logger.error(
            f'Call {ISSIGNED_URL}/{request_obj.token} gave {cons_req.status_code} with {json.dumps(cons_req.text)}')

    request_obj.save()


def _gen_desc_op(id):
    operation_view = {}
    operation_view['key'] = id
    operation_view['text'] = myConfig.get_operation_obj(id).text
    operation_view['description'] = myConfig.get_operation_obj(id).description
    return operation_view


def _gen_operations(operations):
    # mySerializedOperations.reset()
    mySerializedOperations.unserialize(operations)
    operations_view = []
    for operation in mySerializedOperations.operations:
        operation_view = _gen_desc_op(operation['key'])
        operation_view['chosen_option'] = operation['chosen_option']
        operation_view['reply'] = operation['reply']
        opt_obj = myConfig.get_option_obj(operation['chosen_option'])
        if not opt_obj == None:
            operation_view['chosen_option_text'] = opt_obj.text

        operations_view.append(operation_view)
    return operations_view


def _gen_queryset(pk):
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

    for request_obj in request_set:
        _update_request(request_obj)
        logger.debug(f'Request {request_obj.id} updated')
        request_view = {}
        request_view['id'] = request_obj.id
        request_view['token'] = request_obj.token
        request_view['text'] = request_obj.text
        request_view['description'] = request_obj.description
        # request_view['user_id'] = request_obj.user_id
        request_view['status'] = request_obj.status
        request_view['signature'] = request_obj.signature

        operations_view = _gen_operations(request_obj.operations)

        request_view['operations'] = operations_view
        logger.debug(f'Operations added: {json.dumps(operations_view)}')
        # print(f"view operations {json.dumps(request_view['operations'])}")

        requests_view.append(request_view)
        logger.debug(f'Request added: {json.dumps(request_view)}')

    if not pk == None:
        #  Return if just one request is needed
        logger.debug(f'Return request: {json.dumps(requests_view[0])}')
        return requests_view[0]

    operations_view = []
    for op_key in myConfig.operations.keys():
        operation_view = {}
        op_obj = myConfig.get_operation_obj(op_key)
        operation_view['key'] = op_obj.key
        operation_view['text'] = op_obj.text
        operations_view.append(operation_view)
        logger.debug(f'Operation added: {json.dumps(operation_view)}')

    my_set = {}
    my_set['requests'] = requests_view
    my_set['operations'] = operations_view
    logger.debug(f'Return queryset: {json.dumps(my_set)}')
    return my_set


# class LoginView(LoginView):
#     template_name = 'researcher_req/login.html'


def logout_view(request):
    logger.debug(f'Logout view request')
    template_name = 'researcher_req/logout.html'
    # breakpoint()
    if request.user.is_authenticated:
        logout(request)
        return render(request, template_name)
    return HttpResponseRedirect(reverse('researcher_req:login'))


def login_view(request):
    logger.debug(f'Login view request')
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('researcher_req:index'))
    template_name = 'researcher_req/login.html'
    # context = {'my_set' : _gen_queryset(None)}
    # logger.debug(f'Index view rendering: {json.dumps(context)}')
    context = {'challenge': labut.generate_random_challenge()}
    return render(request, template_name, context)


@login_required(login_url='researcher_req:login')
def profile_view(request):
    """
        Store information about the researcher
    """
    logger.debug(f'Profile view request')
    template_name = 'researcher_req/profile.html'
    researcher = Researcher.objects.get(user=request.user)
    researcher_obj = {
        "name": f'{researcher.user.first_name} {researcher.user.last_name}',
        "email": researcher.user.email,
        "publickey": researcher.publickey,
        "institute": researcher.institute,
        "institute_publickey": researcher.institute_publickey
    }
    context = {'researcher': researcher_obj}
    logger.debug(f'Profile view rendering: {json.dumps(context)}')
    return render(request, template_name, context)


@login_required(login_url='researcher_req:login')
def index_view(request):
    logger.debug(f'Index view request')
    template_name = 'researcher_req/index.html'
    context = {'my_set': _gen_queryset(None)}
    logger.debug(f'Index view rendering: {json.dumps(context)}')
    return render(request, template_name, context)


@login_required(login_url='researcher_req:login')
def prepare_request_view(request):
    logger.debug(f'New Request view request')
    template_name = 'researcher_req/prepare_request.html'
    context = {'my_set': _gen_queryset(None)}
    return render(request, template_name, context)


@login_required(login_url='researcher_req:login')
def request_view(request, pk):
    logger.debug(f'Request view request')
    template_name = 'researcher_req/request.html'
    context = {'request': _gen_queryset(pk)}
    logger.debug(f'Request view rendering: {json.dumps(context)}')
    return render(request, template_name, context)


@login_required(login_url='researcher_req:login')
def operation_view(request, key):
    logger.debug(f'Operation view request')
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

    context = {'operation': ope_view}
    logger.debug(f'Operation view rendering: {json.dumps(context)}')
    return render(request, template_name, context)


def check_login(request):
    """
        Check credentials and log user in
    """
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'username' in request.POST and 'challenge' in request.POST and 'response' in request.POST:
            username = request.POST['username']
            challenge = request.POST['challenge']
            response = request.POST['response']
            user = authenticate(request, username=username,
                                is_challenge=True, challenge=challenge, response=response)
            if user is not None:
                login(request, user)

                # Check researcher is associated to user
                if not hasattr(user, 'researcher'):
                    logger.error(f'No associated researcher for user: {user}')
                    return HttpResponseRedirect(reverse('researcher_req:login'))
                    
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('researcher_req:profile'))
    logger.debug(f'Login failed')
    return HttpResponseRedirect(reverse('researcher_req:login'))


def fill_profile(request):
    """
        Save researcher information
    """
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')

    researcher = Researcher.objects.get(user=request.user)
    if request.method == 'POST':
        if 'publickey' in request.POST:
            researcher.publickey = request.POST['publickey']
        if 'institute' in request.POST:
            researcher.institute = request.POST['institute']
        if 'institute_publickey' in request.POST:
            researcher.institute_publickey = request.POST['institute_publickey']
        researcher.save()

    return HttpResponseRedirect(reverse('researcher_req:index'))


@login_required(login_url='researcher_req:login')
def sign_request(request):
    """
        Prepare new request(s) to be signed
    """
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        web_data = request.POST
        if 'name' in web_data and 'description' in web_data and 'operations' in web_data and 'nr_users' in web_data:
            # print(f'request {web_data}')
            operations_ids = web_data.getlist('operations')

            operations = [_gen_desc_op(id) for id in operations_ids]

            nr_users = int(web_data.get('nr_users'))

            tokens = [labut.gen_token(web_data.get('name'), web_data.get(
                'description'), operations_ids) for _ in range(nr_users)]

            new_request = {
                "name": web_data.get('name'),
                "description": web_data.get('description'),
                "nr_users": nr_users,
                "operations": operations,
                "tokens": tokens
            }
            template_name = 'researcher_req/sign_request.html'
            context = {'request': new_request}
            return render(request, template_name, context)
    logger.debug(
        f'{inspect.currentframe().f_code.co_name} returning without action')
    return HttpResponseRedirect(reverse('researcher_req:prepare_request'))


@login_required(login_url='researcher_req:login')
def store_request(request):
    """
        Generate and store the new request
    """
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        web_data = request.POST
        if 'name' in web_data and 'description' in web_data and 'operations' in web_data and 'token' in web_data:
            
            researcher = Researcher.objects.get(user=request.user)
            
            tokens = web_data.getlist('token')
            for token in tokens:
                new_request = Request(text=web_data.get('name'), description=web_data.get(
                    'description'), researcher=researcher)

                # Add operations to request
                operations_ids = web_data.getlist('operations')

                mySerializedOperations.reset()
                for id in operations_ids:
                    mySerializedOperations.add_operation_key(id)
                    # print(f'operation key: {ope_obj.key}')

                new_request.operations = mySerializedOperations.serialize()

                new_request.token = token
                new_request.signature = web_data.get(f'signature-{token}')
                
                new_request.save()

            return HttpResponseRedirect(reverse('researcher_req:index'))
    logger.debug(
        f'{inspect.currentframe().f_code.co_name} returning without action')
    return HttpResponseRedirect(reverse('researcher_req:index'))


@login_required(login_url='researcher_req:login')
def perform_action(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'Token' in request.POST and 'operationKey' in request.POST:
            token = request.POST.get('Token')
            operationKey = request.POST.get('operationKey')
            # cons_req = requests.get(f'{ISSIGNED_URL}/{request_obj.token}')
            requestInst = get_object_or_404(Request, token=token)

            url = f'{LOGOP_URL}'
            data = {
                'token': token,
                'ope_key': operationKey
            }
            logger.debug(f'Perform request: {url}')
            log_post = requests.post(url, data=data)

            if log_post.status_code == 200:
                logger.info(f'Request returned: {log_post.text}')
                mySerializedOperations.unserialize(requestInst.operations)
                mySerializedOperations.set_reply(operationKey, log_post.text)
                requestInst.operations = mySerializedOperations.serialize()
                requestInst.save()
            else:
                logger.error(
                    f'Request returned: {log_post.status_code}, {log_post.text}')

            return HttpResponseRedirect(reverse('researcher_req:request', args=(requestInst.id,)))
    logger.debug(f'Returning without action')
    return HttpResponseRedirect(reverse('researcher_req:index'))


@login_required(login_url='researcher_req:login')
def download_request(request, id):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    requestInst = get_object_or_404(
        Request, id=id)
    # print(f'request {request.POST}')
    # print(f'operation {operation for operation in requestInst.operations.all()}')

    # payload = requestInst.make_contract()
    payload = requestInst.token
    # response content type
    response = HttpResponse(content_type='text/json')
    # decide the file name
    response['Content-Disposition'] = 'attachment; filename="request.json"'

    response.write(payload)

    return response
