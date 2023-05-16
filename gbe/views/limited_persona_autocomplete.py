from dal import autocomplete
from django.db.models import Q
from gbe.models import Bio
from gbe.functions import validate_profile


class LimitedPersonaAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        profile = validate_profile(self.request, require=True)
        if not profile:
            return Bio.objects.none()

        qs = Bio.objects.filter(contact=profile, multiple_performers=True)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(label__icontains=self.q))

        return qs
