from django.urls import include, path

from . import api

app_name = 'donor_app.api'


urlpatterns = [
    path('is_signed/<str:token>', api.is_signed, name='is_signed'),
    path('allowed_experiments/<str:token>', api.allowed_experiments, name='allowed_experiments'),
    path('log_experiment/', api.log_experiment, name='log_experiment'),
    path('ping/', api.ping, name='ping'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]