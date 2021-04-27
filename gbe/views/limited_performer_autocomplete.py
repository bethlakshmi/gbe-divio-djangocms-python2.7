from dal import autocomplete
from django.db.models import Q
from gbe.models import Performer
from gbe.functions import validate_profile


class LimitedPerformerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        profile = validate_profile(self.request, require=True)
        if not profile:
            return Performer.objects.none()

        qs = Performer.objects.filter(contact=profile)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(label__icontains=self.q))

        return qs
