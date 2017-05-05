from django.contrib import admin

from whim.core.models import Event, Source


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass
