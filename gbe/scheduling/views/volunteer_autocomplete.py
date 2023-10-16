from dal import autocomplete
from django.contrib.auth.mixins import PermissionRequiredMixin
from scheduler.models import Event
from django.db.models import Q
from settings import GBE_DATETIME_FORMAT


class VolunteerAutocomplete(PermissionRequiredMixin,
                            autocomplete.Select2QuerySetView):

    permission_required = 'scheduler.view_event'

    def get_queryset(self):
        label = self.forwarded.get('label', None)

        qs = Event.objects.filter(event_style="Volunteer")

        if label:
            qs = qs.filter(eventlabel__text=label)

        if self.q:
            qs = qs.filter(Q(title__icontains=self.q) |
                           Q(parent__title__icontains=self.q))
        return qs

    def get_result_label(self, result):
        return result.form_label()
