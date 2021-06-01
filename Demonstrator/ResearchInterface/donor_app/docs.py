import json
from rest_framework.response import Response
from rest_framework.decorators import api_view

from donor_app.models import Consent


@api_view((['GET']))
def view_doc(request, doc_id):
    if doc_id is not None:
        try:
            consent = Consent.objects.get(token=doc_id)
        except Consent.DoesNotExist as e:
            return Response({f'error': f'consent {doc_id} does not exist'})
        if consent is not None:
            return Response(json.loads(consent.signed_vc))
    return Response({f'error': f'You need to provide an id'})
