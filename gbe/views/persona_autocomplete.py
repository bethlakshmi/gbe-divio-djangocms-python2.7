from dal import autocomplete
from django.db.models import Q
from gbe.models import Bio
from gbe.functions import validate_profile


class PersonaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not validate_profile(self.request, require=True):
            return Bio.objects.none()

        qs = Bio.objects.filter(
            contact__user_object__is_active=True,
            multiple_performers=False)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(contact__display_name__icontains=self.q) |
                Q(label__icontains=self.q))

        return qs
