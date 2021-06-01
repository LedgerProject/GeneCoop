from django.urls import include, path

from . import ids

app_name = 'donor_app.ids'


urlpatterns = [
    path('<str:id>', ids.view_entity, name='view_entity'),
    path('<user_id>/seed/', ids.gen_seed, name='gen_seed'),
]