from dal import autocomplete

from gbe.models import Persona


class PersonaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Persona.objects.none()

        qs = Persona.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q,
            	           contact__user_object__is_active=True)

        return qs
