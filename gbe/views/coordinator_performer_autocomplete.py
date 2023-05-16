from dal import autocomplete
from django.db.models import Q
from gbe.models import Bio
from gbe.functions import validate_profile
from django.contrib.auth.mixins import PermissionRequiredMixin


class CoordinatorPerformerAutocomplete(PermissionRequiredMixin,
                                       autocomplete.Select2QuerySetView):
    permission_required = 'gbe.view_performer'

    def get_queryset(self):
        qs = Bio.objects.all()

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) |
                Q(label__icontains=self.q))

        return qs
