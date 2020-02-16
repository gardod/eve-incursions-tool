from django.contrib import admin
from waitlist.models import Instance, ShipType, Pilot

class InstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified')

admin.site.register(Instance, InstanceAdmin)
admin.site.register(ShipType, admin.ModelAdmin)
admin.site.register(Pilot, admin.ModelAdmin)