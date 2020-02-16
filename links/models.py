import urllib
from datetime import datetime
from xml.dom import minidom

from django.core.cache import cache
from django.core.mail import mail_admins
from django.db import models

# constant

SCRIPTS = (
    (1, 'Optimal Range'),
    (2, 'Tracking Speed'),
)

GROUPS = (
    (1, 'logi'),
    (2, 'short'),
    (3, 'mid'),
    (4, 'long'),
)

## independent

class Instance(models.Model):
    name = models.CharField(max_length = 20, primary_key = True)
    last_modified = models.DateTimeField(default = datetime.utcnow)
    active_wing = models.CharField(max_length = 10, default = '')
    ignore_squad = models.CharField(max_length = 10, default = '')
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']
    
class ShipType(models.Model):
    name = models.CharField(max_length = 40)
    group = models.SmallIntegerField(choices = GROUPS)
    default_script = models.SmallIntegerField(choices = SCRIPTS, null=True, blank=True)
    default_color = models.CharField(max_length = 10)
    order = models.SmallIntegerField(default = 0)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['order']

class PilotId(models.Model):
    name = models.CharField(max_length = 40)
    char_id = models.CharField(max_length = 20)
    def __unicode__(self):
        return self.name
    class Meta:
        ordering = ['name']

## instance specific

class ShipOption(models.Model):
    instance = models.ForeignKey(Instance)
    ship_type = models.ForeignKey(ShipType)
    script = models.SmallIntegerField(choices = SCRIPTS, null=True, blank=True)
    color = models.CharField(max_length = 10)
    order = models.SmallIntegerField(default = 0)
    def __unicode__(self):
        return u'{0} {1}'.format(unicode(self.instance), unicode(self.ship_type))
    class Meta:
        ordering = ['order']
        
class Pilot(models.Model):
    instance = models.ForeignKey(Instance)
    ship_type = models.ForeignKey(ShipType)
    name = models.CharField(max_length = 40)
    tl = models.SmallIntegerField(default = 0)
    resebo = models.SmallIntegerField(default = 0)
    stable = models.BooleanField(default = False)
    def __unicode__(self):
        return u'{0} {1}'.format(unicode(self.instance), self.name)
    class Meta:
        ordering = ['ship_type', 'name']
    
    def get_id(self):
        cache_key = 'pilot_ids'
        data = cache.get( cache_key )
        if not data:
            data = {}
        
        # id already in cache
        if self.name in data:
            return data[self.name]
        # id already in database, set cache
        try:
            pilot_id = PilotId.objects.get(name = self.name)
            data[self.name] = pilot_id.char_id
            cache.set( cache_key, data )
            return pilot_id.char_id
        except:
            pass
        # retrieve id from API, set database and cache
        try:
            url = 'https://api.eveonline.com/eve/CharacterID.xml.aspx'
            data = { 'names': self.name }
            content = urllib.urlopen(url, urllib.urlencode(data)).read()
            xml = minidom.parseString(content)
            char_id = xml.getElementsByTagName('row')[0].attributes['characterID'].value
            if not PilotId.objects.filter(name = self.name).exists():
                PilotId.objects.create(name = self.name, char_id = char_id)
            data[self.name] = char_id
            cache.set( cache_key, data )
            return char_id
        except Exception as e:
            error_massage = 'ERROR<br>{0}<br>{1} {2}<br>{3}'.format(type(e), e.errno, e.strerror, e)
            mail_admins('API Error', error_massage)

        return 0

class Link(models.Model):
    giver = models.ForeignKey(Pilot, related_name='gives_links_to')
    taker = models.ForeignKey(Pilot, related_name='gets_links_from')
    number = models.SmallIntegerField()
    def __unicode__(self):
        return u'{0} {1}'.format(unicode(self.giver), unicode(self.number))
    class Meta:
        ordering = ['number']

