from dal import autocomplete
from django.db.models import Q
from gbe.models import Persona


class PersonaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Persona.objects.none()

        qs = Persona.objects.filter(
            	contact__user_object__is_active=True)

        if self.q:
            qs = qs.filter(
            	Q(name__icontains=self.q) |
                Q(performer_profile__display_name__icontains=self.q))

        return qs
