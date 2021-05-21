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
from labspace.constants import ISSIGNED_URL, ALLOWEDEXP_URL, LOGEXP_URL

# Get an instance of a logger
logger = logging.getLogger(__name__)
# print(f'Logger {__name__}')

myConfig = labut.ConsentConfig('researcher')
myConfig.read_conf()
mySerializedExperiments = labut.SerializeExperiments(myConfig)


def _update_request(request_obj):
    """
        Checks whether a request has been signed
        and what experiments are allowed
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

            # Check what experiments are allowed with an API call
            logger.debug(
                f'Perform request {ALLOWEDEXP_URL}/{request_obj.token}')
            exp_req = requests.get(f'{ALLOWEDEXP_URL}/{request_obj.token}')

            if exp_req.status_code == 200:
                logger.debug(f'Request result: {exp_req.json()}')
                exp_results = exp_req.json()
                # print(f'op_result: {exp_results}')

                # Read and deserialise experiments contained in the request
                logger.debug(f'Start deserialize experiments')

                mySerializedExperiments.unserialize(request_obj.experiments)
                logger.debug(
                    f'Deserialize experiments: {request_obj.experiments}')

                for op_result in exp_results:
                    # print(f"key: {op_result['key']}")
                    mySerializedExperiments.select_option_key(
                        op_result['key'], op_result['chosen_option'])

                request_obj.experiments = mySerializedExperiments.serialize()
                logger.debug(f'Serialize experiments: {request_obj.experiments}')
            else:
                logger.error(
                    f'Call {ALLOWEDEXP_URL}/{request_obj.token} gave {exp_req.status_code} with {exp_req.text}')
    else:
        logger.error(
            f'Call {ISSIGNED_URL}/{request_obj.token} gave {cons_req.status_code} with {json.dumps(cons_req.text)}')

    request_obj.save()


def _gen_desc_op(id):
    experiment_view = {}
    experiment_view['key'] = id
    experiment_view['name'] = myConfig.get_experiment_obj(id).name
    experiment_view['description'] = myConfig.get_experiment_obj(id).description
    return experiment_view


def _gen_experiments(experiments):
    # mySerializedExperiments.reset()
    mySerializedExperiments.unserialize(experiments)
    experiments_view = []
    for experiment in mySerializedExperiments.experiments:
        experiment_view = _gen_desc_op(experiment['key'])
        experiment_view['chosen_option'] = experiment['chosen_option']
        experiment_view['reply'] = experiment['reply']
        opt_obj = myConfig.get_option_obj(experiment['chosen_option'])
        if not opt_obj == None:
            experiment_view['chosen_option_name'] = opt_obj.name

        experiments_view.append(experiment_view)
    return experiments_view


def _gen_queryset(pk):
    """
        Return the requests, checking whether 
        they have been signed and what experiments
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
        request_view['name'] = request_obj.name
        request_view['description'] = request_obj.description
        # request_view['user_id'] = request_obj.user_id
        request_view['status'] = request_obj.status

        experiments_view = _gen_experiments(request_obj.experiments)

        request_view['experiments'] = experiments_view
        logger.debug(f'Experiments added: {json.dumps(experiments_view)}')
        # print(f"view experiments {json.dumps(request_view['experiments'])}")

        requests_view.append(request_view)
        logger.debug(f'Request added: {json.dumps(request_view)}')

    if not pk == None:
        #  Return if just one request is needed
        logger.debug(f'Return request: {json.dumps(requests_view[0])}')
        return requests_view[0]

    experiments_view = []
    for op_key in myConfig.experiments.keys():
        experiment_view = {}
        op_obj = myConfig.get_experiment_obj(op_key)
        experiment_view['key'] = op_obj.key
        experiment_view['name'] = op_obj.name
        experiments_view.append(experiment_view)
        logger.debug(f'Experiment added: {json.dumps(experiment_view)}')

    my_set = {}
    my_set['requests'] = requests_view
    my_set['experiments'] = experiments_view
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
def experiment_view(request, key):
    logger.debug(f'Experiment view request')
    template_name = 'researcher_req/experiment.html'
    exp_obj = myConfig.get_experiment_obj(key)
    opts_view = []
    for exp_key in exp_obj.options:
        opt_view = {}
        opt_obj = myConfig.get_option_obj(exp_key)
        opt_view['key'] = opt_obj.key
        opt_view['name'] = opt_obj.name
        opts_view.append(opt_view)

    exp_view = {}
    exp_view['options'] = opts_view
    exp_view['name'] = exp_obj.name
    exp_view['description'] = exp_obj.description

    context = {'experiment': exp_view}
    logger.debug(f'Experiment view rendering: {json.dumps(context)}')
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
            user = authenticate(request, is_researcher=True, username=username, challenge=challenge, response=response)
            if user is not None:
                login(request, user)

                # Check researcher is associated to user
                if not hasattr(user, 'researcher'):
                    logger.error(f'No associated researcher for user: {user}')
                    return HttpResponseRedirect(reverse('researcher_req:login'))
                    
                # Redirect to a success page.
                return HttpResponseRedirect(reverse('researcher_req:index'))
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
        if 'name' in web_data and 'description' in web_data and 'experiments' in web_data and 'nr_users' in web_data:
            # print(f'request {web_data}')
            experiments_ids = web_data.getlist('experiments')

            experiments = [_gen_desc_op(id) for id in experiments_ids]

            nr_users = int(web_data.get('nr_users'))

            tokens, token_times = zip(*[labut.gen_token(web_data.get('name'), web_data.get(
                'description'), experiments_ids) for _ in range(nr_users)])
            token_data = []
            # create the structure to pass tokens and times
            for i in range(len(tokens)):
                token_data.append({
                    "token": tokens[i],
                    "token_time": token_times[i]
                })

            new_request = {
                "name": web_data.get('name'),
                "description": web_data.get('description'),
                "nr_users": nr_users,
                "experiments": experiments,
                "token_data": token_data
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
        if 'name' in web_data and 'description' in web_data and 'experiments' in web_data and 'token' in web_data:
            
            researcher = Researcher.objects.get(user=request.user)
            
            tokens = web_data.getlist('token')
            for token in tokens:
                new_request = Request(name=web_data.get('name'), description=web_data.get(
                    'description'), researcher=researcher)

                # Add experiments to request
                experiments_ids = web_data.getlist('experiments')

                mySerializedExperiments.reset()
                for id in experiments_ids:
                    mySerializedExperiments.add_experiment_key(id)
                    # print(f'experiment key: {exp_obj.key}')

                new_request.experiments = mySerializedExperiments.serialize()

                new_request.token = token
                new_request.token_signature = web_data.get(f'signature-{token}')
                new_request.token_time = web_data.get(f'token_time-{token}')
                
                new_request.save()

            return HttpResponseRedirect(reverse('researcher_req:index'))
    logger.debug(
        f'{inspect.currentframe().f_code.co_name} returning without action')
    return HttpResponseRedirect(reverse('researcher_req:index'))


@login_required(login_url='researcher_req:login')
def perform_action(request):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    if request.method == 'POST':
        if 'Token' in request.POST and 'experimentKey' in request.POST:
            token = request.POST.get('Token')
            experimentKey = request.POST.get('experimentKey')
            # cons_req = requests.get(f'{ISSIGNED_URL}/{request_obj.token}')
            requestInst = get_object_or_404(Request, token=token)

            url = f'{LOGEXP_URL}'
            data = {
                'token': token,
                'exp_key': experimentKey
            }
            logger.debug(f'Perform request: {url}')
            log_post = requests.post(url, data=data)

            if log_post.status_code == 200:
                logger.info(f'Request returned: {log_post.text}')
                mySerializedExperiments.unserialize(requestInst.experiments)
                mySerializedExperiments.set_reply(experimentKey, log_post.text)
                requestInst.experiments = mySerializedExperiments.serialize()
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
    # print(f'experiment {experiment for experiment in requestInst.experiments.all()}')

    # payload = requestInst.make_contract()
    payload = requestInst.token
    # response content type
    response = HttpResponse(content_type='text/json')
    # decide the file name
    response['Content-Disposition'] = 'attachment; filename="request.json"'

    response.write(payload)

    return response
