

from django.contrib import admin

from .models import *

class ColorCodingAdmin(admin.ModelAdmin):
    list_display = ['project', 'widget', 'month', 'hard_limit', 'soft_limit']
admin.site.register(ColorCoding,ColorCodingAdmin)

