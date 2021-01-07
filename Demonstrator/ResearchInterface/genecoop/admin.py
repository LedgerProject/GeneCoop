from django.contrib import admin

from .models import Consent, ConsentLogger

admin.site.register(Consent)
admin.site.register(ConsentLogger)
