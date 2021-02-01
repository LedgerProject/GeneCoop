from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Request, Researcher


# Define an inline admin descriptor for Researcher model
# which acts a bit like a singleton
class ResearcherInline(admin.StackedInline):
    model = Researcher
    can_delete = False
    verbose_name_plural = 'researcher'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ResearcherInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Request)


