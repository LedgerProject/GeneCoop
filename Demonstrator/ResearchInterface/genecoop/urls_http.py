from django.urls import path

from . import views

app_name = 'genecoop'

urlpatterns = [
    # path('', views.IndexView.as_view(), name='index'),
    path('', views.index, name='index'),
    # path('<int:pk>/consent', views.ConsentView.as_view(), name='consent'),
    # path('<str:pk>/sign', views.SignConsentView.as_view(), name='sign'),
    path('<str:pk>/sign', views.sign, name='sign'),
    # path('<int:key>/operation/', views.OperationsView.as_view(), name='operation'),
    path('genconsent/', views.genconsent, name='genconsent'),
    path('signconsent/', views.signconsent, name='signconsent'),
    path('<str:pk>/consent', views.consent, name='consent'),
]