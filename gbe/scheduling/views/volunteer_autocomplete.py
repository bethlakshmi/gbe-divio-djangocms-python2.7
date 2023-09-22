from dal import autocomplete
from django.db.models import Q
from scheduler.models import Event
from django.contrib.auth.mixins import PermissionRequiredMixin
from settings import GBE_DATETIME_FORMAT


class VolunteerAutocomplete(PermissionRequiredMixin,
                            autocomplete.Select2QuerySetView):

    permission_required = 'scheduler.view_event'

    def get_queryset(self):
        qs = Event.objects.filter(
            event_style="Volunteer")

        label = self.forwarded.get('label')
        if label:
            qs = qs.filter(eventlabel__text=label)

        if self.q:
            qs = qs.filter(
                Q(title__icontains=self.q) |
                Q(parent__title__icontains=self.q))

        return qs

    def get_result_label(self, result):
        label = "%s - %s" % (result.title,
                             result.starttime.strftime(GBE_DATETIME_FORMAT))
        if result.parent is not None:
            label = result.parent.title + ' - ' + label
        return label
