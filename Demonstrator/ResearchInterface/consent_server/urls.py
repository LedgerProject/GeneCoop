"""consent_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('request/', include('researcher_app.urls')),
    path('consent/', include('donor_app.urls_consent')),
    path('ids/', include('id_app.urls_ids')),
    path('docs/', include('donor_app.urls_docs')),
    path('data/', include('datasafe_app.urls')),
    path('admin/', admin.site.urls),
]
