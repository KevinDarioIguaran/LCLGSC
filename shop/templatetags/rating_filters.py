from django import template

register = template.Library()

@register.filter
def star_percent(percentages_dict, star):
    """Retorna el porcentaje de calificaciones para una estrella específica (como string)."""
    key = f"{star}_stars_percent"
    return percentages_dict.get(key, 0)
