from django.urls import path, include

from . import views

app_name = 'genecoop'

urlpatterns = [
    path('', views.index_view, name='index'),

    path('login/', views.login_view, name='login'),
    path('check_login/', views.check_login, name='check_login'),
    
    path('token/', views.token_view, name='token'),
    path('check_token/', views.check_token, name='check_token'),

    path('<str:token>/choose', views.choose_view, name='choose'),
    path('gen_consent/', views.gen_consent, name='gen_consent'),
    path('<str:token>/sign', views.sign_view, name='sign'),
    path('sign_consent', views.sign_consent, name='sign_consent'),
    
    path('<str:pk>/consent', views.consent_view, name='consent'),
    
    # path('verify_consent/', views.verify_consent, name='verify_consent'),
    

    path('api/', include('genecoop.urls_api'))
]