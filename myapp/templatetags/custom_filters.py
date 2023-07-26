from django import template

register = template.Library()

@register.filter
def is_not_friends(user, viewed_user):
    return not user.friends.filter(id=viewed_user.id).exists()
