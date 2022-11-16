from django.contrib import admin
from .models import Portal
from django.db import models
from tinymce.widgets import TinyMCE


# Register your models here.
class PortalAdmin(admin.ModelAdmin):

    fieldsets = [
        ("Name", {'fields' : ["portal_name"]}),
        ("Slug", {'fields': ["portal_slug"]}),
        ("URL", {'fields': ["portal_url"]}),
        ("Publisher", {'fields': ["portal_publisher"]}),
        ("Director", {'fields': ["portal_director"]}),
        ("Editor-in-chief", {'fields': ["portal_editor_in_chief"]}),
        ("About portal", {'fields': ["portal_about_us"]}),
        ("Logo", {'fields': ["portal_logo"]})
    ]

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    }


admin.site.register(Portal, PortalAdmin)