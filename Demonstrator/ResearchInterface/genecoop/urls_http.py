from django.urls import path, include

from . import views

app_name = 'genecoop'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('token/', views.token_view, name='token'),
    path('<str:pk>/consent', views.consent_view, name='consent'),
    path('<str:token>/sign', views.sign_view, name='sign'),
    path('check_token/', views.check_token, name='check_token'),
    path('verify_consent/', views.verify_consent, name='verify_consent'),
    path('sign_consent/', views.sign_consent, name='sign_consent'),
    path('api/', include('genecoop.urls_api'))
]