import re
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseServerError
from django.utils import simplejson
from django.core.cache import cache
from django.db import transaction
from django.core.mail import mail_admins

from links.models import Instance, ShipType, ShipOption, Pilot, Link

LOCKED_INSTANCES = []

# views

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        error = check_instance_name(name)
        if not error:
            create_instance(name)
            return redirect(reverse(edit, args = [name]))
        else:
            return render(request, 'links/index.html', {'error': error})
    else:
        return render(request, 'links/index.html')

def view(request, name):
    instance = get_object_or_404(Instance, name = name)
    return render(request, 'links/view.html', get_data(instance))

def edit(request, name):
    instance = get_object_or_404(Instance, name = name)
    return render(request, 'links/edit.html', get_data(instance))

@csrf_exempt
@require_POST
def commit(request, name):
    instance = get_object_or_404(Instance, name = name)
    
    if instance in LOCKED_INSTANCES:
        return HttpResponse('INSTANCE LOCKED')
    else:
        try:
            LOCKED_INSTANCES.append(instance)
            
            dps  = simplejson.loads( request.POST['dps']  )
            logi = simplejson.loads( request.POST['logi'] )
            config = simplejson.loads( request.POST['config'] )
            
            instance.last_modified = datetime.utcnow()
            instance.active_wing   = request.POST['active_wing']
            instance.ignore_squad  = request.POST['ignore_squad']
            instance.save()
            
            with transaction.commit_on_success():
                old_pilots = get_pilots(instance)
                for old_pilot in old_pilots:
                    old_pilot.delete()
            
            with transaction.commit_on_success():
                for pilot_name, ship_type in dps.items():
                    Pilot.objects.create(
                        instance = instance,
                        ship_type = get_ship_type(ship_type),
                        name = pilot_name,
                    )
            with transaction.commit_on_success():
                for pilot_name, data in logi.items():
                    logi_pilot = Pilot.objects.create(
                        instance = instance,
                        ship_type = get_ship_type(data['ship_type']),
                        name = pilot_name,
                        tl = data['tl'],
                        resebo = data['resebo'],
                        stable = data['stable'],
                    )
                    for index, linked_pilot in enumerate( data['links'] ):
                        Link.objects.create(
                            giver = logi_pilot,
                            taker = Pilot.objects.get(instance = instance, name = linked_pilot),
                            number = index
                        )
            with transaction.commit_on_success():
                ship_options = get_ship_options(instance)
                for ship_type_name, data in config.items():
                    for ship_option in ship_options:
                        if ship_option.ship_type.name == ship_type_name:
                            break
        
                    ship_option.color = data['color']
                    try:
                        ship_option.script = int( data['script'] )
                    except:
                        ship_option.script = None
                    ship_option.save()
                
            cache.delete( 'links_{0}_pilots'.format(instance.name) )
            cache.delete( 'links_{0}_ship_options'.format(instance.name) )
        except Exception as e:
            error_massage = 'ERROR<br>{0}<br>{1} {2}<br>{3}'.format(type(e), e.errno, e.strerror, e)
            mail_admins('Commit Error', error_massage)
            return HttpResponseServerError( error_massage )
        finally:
            LOCKED_INSTANCES.remove(instance)
    
    return HttpResponse('OK')

def howto(request):
    return render(request, 'links/howto.html')


# helper functions

def check_instance_name(name):
    error = None
    if re.match('^[0-9A-Za-z_\-]+$', name):
        if Instance.objects.filter(name = name).exists():
            error = 'Name is already in use<br><a href='+reverse(view, args = [name])+'>View</a> <a href='+reverse(edit, args = [name])+'>Edit</a>'
    else:
        error = 'Name can only contain alphanumeric characters, "-", and "_"'
    return error

def get_ship_options(instance):
    key = 'links_{0}_ship_options'.format(instance.name)
    data = cache.get( key )
    if data:
        return data
    data = list( instance.shipoption_set.all() )
    cache.set( key, data )
    return data
    
def get_pilots(instance):
    key = 'links_{0}_pilots'.format(instance.name)
    data = cache.get( key )
    if data:
        return data
    data = list( instance.pilot_set.all() )
    cache.set( key, data )
    return data

def get_ship_type(name):
    key = 'links_ship_type'
    data = cache.get( key )
    if data:
        return data[ name ]
    data = {}
    ship_types = list( ShipType.objects.all() )
    for ship_type in ship_types:
        data[ ship_type.name ] = ship_type
    cache.set( key, data )
    return data[ name ]

def get_ship_types():
    key = 'links_ship_type'
    data = cache.get( key )
    if data:
        return data
    data = {}
    ship_types = list( ShipType.objects.all() )
    for ship_type in ship_types:
        data[ ship_type.name ] = ship_type
    cache.set( key, data )
    return data

# heavy load functions

def create_instance(name):
    instance = Instance.objects.create(name=name)
    for name, ship_type in get_ship_types().items():
        ShipOption.objects.create(
            instance = instance,
            ship_type = ship_type,
            script = ship_type.default_script,
            color = ship_type.default_color,
            order = ship_type.order
        )

def get_data(instance):
    ship_options = get_ship_options(instance)
    pilots = get_pilots(instance)

    pilots_long = [ pilot for pilot in pilots if pilot.ship_type.get_group_display() == 'long' ]
    pilots_mid = [ pilot for pilot in pilots if pilot.ship_type.get_group_display() == 'mid' ]
    pilots_short = [ pilot for pilot in pilots if pilot.ship_type.get_group_display() == 'short' ]
    pilots_logi_raw = [ pilot for pilot in pilots if pilot.ship_type.get_group_display() == 'logi' ]
    
    pilots_logi = []
    for pilot in pilots_logi_raw:
        links = []
        for link in list( pilot.gives_links_to.all() ):
            links.append( link.taker )
        pilots_logi.append({
            'pilot': pilot,
            'links': links
        })

    return {
        'name': instance.name,
        'ships': ship_options,
        'long': pilots_long,
        'mid': pilots_mid,
        'short': pilots_short,
        'logi': pilots_logi,
        'active_wing': instance.active_wing,
        'ignore_squad': instance.ignore_squad
    }
    


