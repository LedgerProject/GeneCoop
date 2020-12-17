from django.urls import path

from . import views

app_name = 'genecoop'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/sign', views.ConsentView.as_view(), name='sign'),
    # path('<int:key>/operation/', views.OperationsView.as_view(), name='operation'),
    # path('addrequest/', views.addrequest, name='addrequest'),
    path('genconsent/', views.genconsent, name='genconsent'),
]