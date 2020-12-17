from django.contrib import admin

from .models import Request, Operation, Option

admin.site.register(Operation)
admin.site.register(Option)
admin.site.register(Request)

