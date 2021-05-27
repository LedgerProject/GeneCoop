from django.urls import include, path

from . import docs

app_name = 'donor_app.docs'


urlpatterns = [
    path('<str:doc_id>', docs.view_doc, name='view_doc'),
]