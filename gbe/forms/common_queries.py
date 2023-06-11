from gbe.models import (
    Bio,
    Profile,
)


visible_personas = Bio.objects.filter(
    contact__user_object__is_active=True)


visible_profiles = Profile.objects.filter(
    user_object__is_active=True).exclude(
    display_name='')
