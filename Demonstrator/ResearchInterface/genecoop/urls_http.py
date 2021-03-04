from django.urls import path, include

from . import views

app_name = 'genecoop'

urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    path('landing/', views.landing_view, name='landing'),
    path('', views.index_view, name='index'),
    # path('<int:pk>/consent', views.ConsentView.as_view(), name='consent'),
    # path('<str:pk>/sign', views.SignConsentView.as_view(), name='sign'),
    path('<str:pk>/sign', views.sign_view, name='sign'),
    # path('<int:key>/operation/', views.OperationsView.as_view(), name='operation'),
    path('verify_consent/', views.verify_consent, name='verify_consent'),
    path('sign_consent/', views.sign_consent, name='sign_consent'),
    path('<str:pk>/consent', views.consent_view, name='consent'),
    path('api/', include('genecoop.urls_api'))
]