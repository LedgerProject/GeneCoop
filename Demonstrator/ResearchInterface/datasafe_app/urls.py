from django.urls import path, re_path

from . import views

app_name = 'datasafe_app'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('retrieve_vc/', views.retrieve_vc, name='retrieve_vc'),
    path('<str:token>/', views.vc_view, name='vc'),
    
]