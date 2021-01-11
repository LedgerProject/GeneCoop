from django.urls import path

from . import views

app_name = 'researcher_req'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('<int:pk>/', views.request_view, name='request'),
    path('<str:key>/operation/', views.operation_view, name='operation'),
    path('add_request/', views.add_request, name='add_request'),
    path('generate_token/', views.generate_token, name='generate_token'),
    path('perform_action/', views.perform_action, name='perform_action'),
]