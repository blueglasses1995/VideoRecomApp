from django.contrib import admin
from . import models
# Register your models here.


@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('username', )


admin.site.site_header = "Movie Manage Admin"
admin.site.site_title = "Movie Manage Admin Portal"
admin.site.index_title = "Welcome to Movie Manage Admin Portal"
