from django.urls import path

from . import views

app_name = 'researcher_req'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:pk>/', views.request, name='request'),
    path('<str:key>/operation/', views.operation, name='operation'),
    path('addrequest/', views.addrequest, name='addrequest'),
    path('gentoken/', views.gentoken, name='gentoken'),
]