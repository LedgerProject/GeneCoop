from django.urls import include, path

from . import api

app_name = 'genecoop.api'


urlpatterns = [
    path('is_signed/<str:token>', api.is_signed, name='is_signed'),
    path('allowed_operations/<str:token>', api.allowed_operations, name='allowed_operations'),
    path('log_operation/<str:token>/<str:operation>', api.log_operation, name='log_operation'),
    path('ping/', api.ping, name='ping'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]