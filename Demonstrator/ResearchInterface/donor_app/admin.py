from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Consent, ConsentLogger

admin.site.register(User, UserAdmin)
admin.site.register(Consent)
admin.site.register(ConsentLogger)
