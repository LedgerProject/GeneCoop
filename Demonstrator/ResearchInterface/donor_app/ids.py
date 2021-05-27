import json
from rest_framework.response import Response
from rest_framework.decorators import api_view

from researcher_app.models import User


@api_view((['GET']))
def view_entity(request, id):
    if id is not None:
        try:
            user = User.objects.get(username=id)
        except User.DoesNotExist as e:
            return Response({f'error': f'user {id} does not exist'})
        if user is not None:
            return Response(user.public_key)
    return Response({f'error': f'You need to provide an id'})
