import json
from rest_framework.response import Response
from rest_framework.decorators import api_view

import consent_server.utils as labut
from donor_app.models import User


@api_view((['GET']))
def view_entity(request, id):
    if id is not None:
        try:
            user = User.objects.get(username=id)
        except User.DoesNotExist as e:
            return Response({f'error': f'user {id} does not exist'})
        if user is not None:
            return Response({"public_key": user.publickey})
    return Response({f'error': f'You need to provide an id'})

@api_view((['POST']))
def gen_seed(request, user_id):
    body = json.loads(request.body.decode("utf-8"))
    if 'message' in body:
        userData = body['message']['hashedQandA']
    else:
        return Response({f'error': f'You need to provide data'})
    if user_id is not None:
        try:
            user = User.objects.get(username=user_id)
        except User.DoesNotExist as e:
            user = User(username=user_id)
            # assign the questions/answers for retrieval later
            user.assign_qa(userData)
            user.save()
            seed = labut.generate_seed(userData)
            return Response({f'seed': seed})
        if user.check_qa(userData):
            seed = labut.generate_seed(userData)
            return Response({f'seed': seed})
        else:
            return Response({f'error': f'Your questions and/or answers are incorrect'})        
    return Response({f'error': f'You need to provide an id'})
