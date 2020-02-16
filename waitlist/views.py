import re
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from waitlist.models import Instance, ShipType, Pilot


# views

def index(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        error = check_instance_name(name)
        if not error:
            Instance.objects.create(name=name)
            return redirect(reverse(status, args = [name]))
        else:
            return render(request, 'waitlist/index.html', {'error': error})
    else:
        return render(request, 'waitlist/index.html')

def view(request, name):
    instance = get_object_or_404(Instance, name = name)
    
    data = { 'name': name }
    if 'HTTP_EVE_TRUSTED' in request.META:
        if request.META['HTTP_EVE_TRUSTED'] == 'Yes':
            pilot_name = request.META['HTTP_EVE_CHARNAME']
            ship_type_name = request.META['HTTP_EVE_SHIPTYPENAME'].lower()
            
            data['pilot_name'] = pilot_name
            try:
                #if on wait list display position
                pilot = instance.pilot_set.get(name = pilot_name)
                logi_wl = list( instance.pilot_set.filter(ship_type__group = 1).distinct() )
                dps_wl  = list( instance.pilot_set.filter(ship_type__group = 2).distinct() )
                
                data['logi_wl'] = unicode( logi_wl.index(pilot)+1 ) if pilot in logi_wl else '-'
                data['dps_wl']  = unicode(  dps_wl.index(pilot)+1 ) if pilot in dps_wl  else '-'
            except:
                #if not on wait list display form
                ship_types = get_ship_types_dict()
                if ship_type_name in ship_types:
                    ship_type = ship_types[ship_type_name]
                else:
                    ship_type = ship_types['other']
                
                data['ship_types'] = get_ship_types()
                data['ship_type']  = ship_type
        else:
            data['error'] = 'Set the site as trusted and refresh'
    else:
        data['error'] = 'Please open the site in IGB'
    
    return render(request, 'waitlist/view.html', data)

@require_POST
def join(request, name):
    instance = get_object_or_404(Instance, name = name)
    pilot_name = request.META['HTTP_EVE_CHARNAME']
    selected_ships = request.POST.getlist('ship')
    
    pilot = Pilot.objects.create(
        instance = instance,
        name = pilot_name
    )
    ship_types = get_ship_types_dict()
    for ship_type_name in selected_ships:
        ship_type = ship_types[ship_type_name]
        pilot.ship_type.add(ship_type)
    
    return redirect(view, name)

@require_POST
def leave(request, name):
    instance = get_object_or_404(Instance, name = name)
    pilot_name = request.META['HTTP_EVE_CHARNAME']
    
    try:
        pilot = Pilot.objects.get(
            instance = instance,
            name = pilot_name
        )
        pilot.delete()
    except:
        pass
    
    return redirect(view, name)

def status(request, name):
    instance = get_object_or_404(Instance, name = name)
    instance.last_modified = datetime.utcnow()
    instance.save()
    
    data = { 'name': name }
    
    data['logi_wl'] = list( instance.pilot_set.filter(ship_type__group = 1).distinct() )
    data['dps_wl']  = list( instance.pilot_set.filter(ship_type__group = 2).distinct() )
    
    return render(request, 'waitlist/status.html', data)

@csrf_exempt
@require_POST
def remove(request, name):
    instance = get_object_or_404(Instance, name = name)
    pilot_name = request.POST.get('name')
    
    try:
        pilot = Pilot.objects.get(
            instance = instance,
            name = pilot_name
        )
        pilot.delete()
    except:
        pass
    
    return HttpResponse('OK');


# helper functions

def check_instance_name(name):
    error = None
    if re.match('^[0-9A-Za-z_\-]+$', name):
        if Instance.objects.filter(name = name).exists():
            error = 'Name is already in use'
    else:
        error = 'Name can only contain alphanumeric characters, "-", and "_"'
    return error

def get_ship_types():
    key = 'waitlist_ship_type'
    data = cache.get( key )
    if data:
        return data
    data = list( ShipType.objects.all() )
    cache.set( key, data )
    return data

def get_ship_types_dict():
    key = 'waitlist_ship_type_dict'
    data = cache.get( key )
    if data:
        return data
    data = {}
    ship_types = get_ship_types()
    for ship_type in ship_types:
        data[ ship_type.name ] = ship_type
    cache.set( key, data )
    return data




