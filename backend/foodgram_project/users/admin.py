from django.contrib import admin
from users.models import CustomUser, Follow

admin.site.register(Follow)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
