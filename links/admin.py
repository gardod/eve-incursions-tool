from django.contrib import admin
from links.models import Instance, ShipType, ShipOption, Pilot, Link, PilotId

class InstanceAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified')

admin.site.register(Instance, InstanceAdmin)
admin.site.register(ShipType, admin.ModelAdmin)
admin.site.register(ShipOption, admin.ModelAdmin)
admin.site.register(Pilot, admin.ModelAdmin)
admin.site.register(Link, admin.ModelAdmin)
admin.site.register(PilotId, admin.ModelAdmin)