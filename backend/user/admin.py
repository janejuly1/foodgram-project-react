from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    # list_display = (
    #     'username',
    #     'first_name',
    #     'last_name',
    #     'email',
    #     'bio',
    #     'role',
    # )
    list_filter = ('email', 'username')

admin.site.register(User, UserAdmin)
