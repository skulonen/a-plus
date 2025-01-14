from django.contrib import admin

from external_services.models import LTIService, LinkService, MenuItem


class LinkServiceAdmin(admin.ModelAdmin):
    search_fields = (
        'url',
        'menu_label',
    )
    list_display_links = ('id',)
    list_display = (
        'id',
        'menu_label',
        'url',
        'destination_region',
        'content_type',
        'enabled',
    )
    readonly_fields = ('content_type',)

class LTIServiceAdmin(admin.ModelAdmin):
    search_fields = (
        'url',
        'menu_label',
    )
    list_display_links = ('id',)
    list_display = (
        'id',
        'menu_label',
        'url',
        'destination_region',
    )

class MenuItemAdmin(admin.ModelAdmin):
    search_fields = (
        'course_instance__instance_name',
        'menu_url',
        'menu_label',
    )
    list_display_links = ('id',)
    list_display = (
        'id',
        'course_instance',
        'service',
        'menu_url',
        'menu_label',
        'enabled',
    )

admin.site.register(LTIService, LTIServiceAdmin)
admin.site.register(LinkService, LinkServiceAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
