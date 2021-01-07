from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.decorators import api_view

from .models import Consent, ConsentLogger
import labspace.utils as labut

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



myConfig = labut.ConsentConfig('user')
myConfig.read_conf()
mySerializedOperations = labut.SerializeOperations(myConfig)

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
def allowed_operations(request, token):
    # print(f'token {token}')
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if consent is not None:
            consent_logger = consent.consentlogger_set.create()
            op_results = []
            
            mySerializedOperations.unserialize(consent.operations)
            for operation in mySerializedOperations.operations:
                op_result = {}
                op_result['key'] = operation['key']
                op_result['chosen_option'] = operation['chosen_option']
                op_results.append(op_result)
            # print(op_results)
            consent_logger.log_allowed_operations(token, op_results)
            consent_logger.save()
            return Response(op_results)
    return Response({f'error': f'You need to provide a token'})
        
@api_view((['POST']))
def log_operation(request, token, ope_key):
    # print(f'token {token}')
    if token is None or ope_key is None:
        return Response({f'error': f'Need to provide both consent and operation'})
    
    if token is not None:
        try:
            consent = Consent.objects.get(token=token)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {token} does not exist'})
        if ope_key is not None:
            consent_logger = consent.consentlogger_set.create()
            mySerializedOperations.unserialize(consent.operations)
            for ope_json in mySerializedOperations.operations:
                if ope_json['key'] == ope_key:
                    if ope_json['chosen_option'] != 1:
                        is_allowed = myConfig.is_op_allowed(ope_json['key'], ope_json['chosen_option'])
                        consent_logger.log_operation(token, ope_key, is_allowed)
                        consent_logger.save()
                        if not is_allowed:
                            return Response({f'error': f'Operation {ope_key} is not allowed for consent {token}'})    
                    else:
                        consent_logger.log_not_signed_operation(token, ope_key)
                        consent_logger.save()
                        return Response({f'error': f'Operation {ope_key} has not been signed'})
        else:
            return Response({f'error': f'Need to provide an operation'})    
    else:
        return Response({f'error': f'Need to provide a token'})
        
