from django.db import models
from datetime import datetime

# constant

GROUPS = (
    (1, 'logi'),
    (2, 'dps'),
)

## independent

class Instance(models.Model):
    name = models.CharField(max_length = 20, primary_key = True)
    last_modified = models.DateTimeField(default = datetime.utcnow)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
class ShipType(models.Model):
    name = models.CharField(max_length = 40)
    group = models.SmallIntegerField(choices = GROUPS)
    order = models.SmallIntegerField(default = 0)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['order']

## instance specific
        
class Pilot(models.Model):
    instance = models.ForeignKey(Instance)
    ship_type = models.ManyToManyField(ShipType)
    name = models.CharField(max_length = 40)
    order = models.AutoField(primary_key=True)
    def __unicode__(self):
        return u'{0} {1}'.format(unicode(self.instance), self.name)
    class Meta:
        ordering = ['instance', 'order']
        

