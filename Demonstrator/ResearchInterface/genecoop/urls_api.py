from django.urls import include, path

from . import views

app_name = 'genecoop.api'


urlpatterns = [
    path('is_signed/<str:token>', views.is_signed, name='is_signed'),
    path('ping/', views.ping, name='ping'),
    path('auth/', include('rest_framework.urls', namespace='rest_framework'))
]