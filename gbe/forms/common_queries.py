from gbe.models import (
    Performer,
    Persona,
    Profile,
)


visible_personas = Persona.objects.filter(
    contact__user_object__is_active=True)


visible_profiles = Profile.objects.filter(
    user_object__is_active=True).exclude(
    display_name='')
