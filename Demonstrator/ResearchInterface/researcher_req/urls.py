from django.urls import path

from . import views

app_name = 'researcher_req'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.RequestView.as_view(), name='request'),
    path('<int:key>/operation/', views.OperationsView.as_view(), name='operation'),
    path('addrequest/', views.addrequest, name='addrequest'),
]