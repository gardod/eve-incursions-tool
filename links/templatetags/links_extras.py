from django import template

register = template.Library()


# General purpose

@register.filter
def get_range(number):
    return range(number)

@register.filter
def get_range_to(low, high):
    return range(low, high)

@register.filter
def get_item(dictionary, key):
    return dictionary[key]

@register.filter
def enum(lst):
    return enumerate(lst)


# Specific

@register.filter
def get_nth_pilot_name(pilots, number):
    return pilots[number].name

@register.filter
def get_nth_pilot_ship_type(pilots, number):
    return pilots[number].ship_type.name