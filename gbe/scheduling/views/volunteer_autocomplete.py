from dal import autocomplete
from django.db.models import Q
from scheduler.models import Event
from django.contrib.auth.mixins import PermissionRequiredMixin


class VolunteerAutocomplete(PermissionRequiredMixin,
                            autocomplete.Select2QuerySetView):

    permission_required = 'scheduler.view_event'

    def get_queryset(self):
        qs = Event.objects.filter(
            event_style="Volunteer")

        if self.q:
            qs = qs.filter(
                Q(title__icontains=self.q) |
                Q(parent__title__icontains=self.q))

        return qs
