from django import template

register = template.Library()

@register.inclusion_tag('components/star_rating.html')
def render_star_rating(average_rating):
    full_stars = int(average_rating)
    half_star = 1 if average_rating - full_stars >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return {
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
    }
