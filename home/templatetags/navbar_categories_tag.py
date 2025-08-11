from django import template
from shop.models import Category  
register = template.Library()

@register.simple_tag
def navbar_categories():
    """Carga las categorías desde la base de datos"""
    return Category.objects.all()
