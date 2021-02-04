from django.urls import path, re_path

from . import views

app_name = 'researcher_req'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('fill_profile/', views.fill_profile, name='fill_profile'),
    path('', views.index_view, name='index'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('<int:pk>/', views.request_view, name='request'),
    path('<str:key>/operation/', views.operation_view, name='operation'),
    path('check_login/', views.check_login, name='check_login'),
    path('add_request/', views.add_request, name='add_request'),
    path('download_request/<int:id>', views.download_request, name='download_request'),
    path('perform_action/', views.perform_action, name='perform_action'),
    path('sign_request/', views.sign_request, name='sign_request'),
]