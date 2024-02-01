from django.contrib import admin

# Register your models here.

from .models import Menu, MenuNode

admin.site.register(Menu)
admin.site.register(MenuNode)