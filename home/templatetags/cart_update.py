from django import template

register = template.Library()

@register.filter
def get_item_update(dictionary, key):
    return dictionary.get(key)
