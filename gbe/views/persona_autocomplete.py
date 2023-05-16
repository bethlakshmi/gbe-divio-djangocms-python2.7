from dal import autocomplete
from django.db.models import Q
from gbe.models import Persona
from gbe.functions import validate_profile


class PersonaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not validate_profile(self.request, require=True):
            return Persona.objects.none()

        qs = Persona.objects.filter(
            contact__user_object__is_active=True)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(performer_profile__display_name__icontains=self.q) |
                Q(label__icontains=self.q))

        return qs
