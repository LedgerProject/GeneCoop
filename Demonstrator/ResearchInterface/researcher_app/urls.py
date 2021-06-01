from django.urls import path, re_path

from . import views

app_name = 'researcher_app'

urlpatterns = [
    path('', views.index_view, name='index'),

    path('login/', views.login_view, name='login'),
    path('check_login/', views.check_login, name='check_login'),

    path('logout/', views.logout_view, name='logout'),
    
    path('profile/', views.profile_view, name='profile'),
    path('fill_profile/', views.fill_profile, name='fill_profile'),
    
    
    path('prepare_request/', views.prepare_request_view, name='prepare_request'),
    path('sign_request/', views.sign_request, name='sign_request'),
    path('store_request/', views.store_request, name='store_request'),
    
    
    path('<int:pk>/', views.request_view, name='request'),
    path('<str:token>/', views.vc_view, name='vc'),
    
    path('perform_action/', views.perform_action, name='perform_action'),

    path('<str:key>/experiment/', views.experiment_view, name='experiment'),    

    path('download_request/<int:id>', views.download_request, name='download_request'),
]