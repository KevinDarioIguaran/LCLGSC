from django import template

register = template.Library()

@register.filter
def get_item_dict_percentage(dictionary, key):
    return dictionary.get(key)
