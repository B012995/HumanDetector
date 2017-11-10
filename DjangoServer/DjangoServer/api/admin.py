from django.contrib import admin

from .models import Count
# Register your models here.

@admin.register(Count)
class Count(admin.ModelAdmin):
    pass