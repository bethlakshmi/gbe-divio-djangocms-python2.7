from dal import autocomplete
from django.db.models import Q
from gbe.models import Business
from gbe.functions import validate_profile


class LimitedBusinessAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        profile = validate_profile(self.request, require=True)
        if not profile:
            return Business.objects.none()

        qs = Business.objects.filter(owners=profile)

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q))

        return qs
