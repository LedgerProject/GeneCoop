from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view

from .models import Consent
import consent_server.utils as labut

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



myConfig = labut.read_conf('user')
mySerializedExperiments = labut.SerializeExperiments(myConfig)

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
            consent_logger = consent.consentlogger_set.create()
            consent_logger.log_is_signed(token)
            consent_logger.save()
            return Response({"token" : token,
                              "signed" : consent.is_signed()})
    return Response({f'error': f'You need to provide a token'})
        
@api_view((['GET']))
def allowed_experiments(request, token):
    # print(f'token {token}')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if consent is not None:
            consent_logger = consent.consentlogger_set.create()
            op_results = []
            
            mySerializedExperiments.unserialize(consent.experiments)
            for experiment in mySerializedExperiments.experiments:
                op_result = {}
                op_result['key'] = experiment['key']
                op_result['chosen_option'] = experiment['chosen_option']
                op_results.append(op_result)
            # print(op_results)
            consent_logger.log_allowed_experiments(token, op_results)
            consent_logger.save()
            return Response(op_results)
    return Response({f'error': f'You need to provide a token'})
        
@api_view((['POST']))
def log_experiment(request):

    if not ('token' in request.POST and 'exp_key' in request.POST):
        return Response({f'error': f'Need to provide both token and experiment'})
    
    token = request.POST.get('token')
    exp_key = request.POST.get('exp_key')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        
        if exp_key is not None:  
            mySerializedExperiments.unserialize(consent.experiments)
            for exp_json in mySerializedExperiments.experiments:
                if exp_json['key'] == exp_key:
                    consent_logger = consent.consentlogger_set.create()
                    if exp_json['chosen_option'] != 1:
                        is_allowed = myConfig.is_exp_allowed(exp_json['key'], exp_json['chosen_option'])
                        consent_logger.log_experiment(token, exp_key, is_allowed)
                        consent_logger.save()
                        if not is_allowed:
                            return Response({f'error': f'Experiment {exp_key} is not allowed, consent {token}'})
                        else:
                            return Response({f'text': f'Experiment {exp_key} was allowed and has been logged, consent {token}'})
                    else:
                        consent_logger.log_not_signed_experiment(token, exp_key)
                        consent_logger.save()
                        return Response({f'error': f'User has not replied to experiment {exp_key}, consent {token}'})
            return Response({f'error': f'exp_key {exp_key} is not found in consent {token} with experiments {mySerializedExperiments.experiments}'})
        else:
            return Response({f'error': f'Need to provide an experiment'})    
    else:
        return Response({f'error': f'Need to provide a token'})
        
