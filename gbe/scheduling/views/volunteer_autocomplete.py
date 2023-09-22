from dal import autocomplete
from django.contrib.auth.mixins import PermissionRequiredMixin
from scheduler.idd import get_event_list


class VolunteerAutocomplete(PermissionRequiredMixin,
                            autocomplete.Select2ListView):

    permission_required = 'scheduler.view_event'

    def get_list(self):
        text = None

        label = self.forwarded.get('label', None)

        if self.q:
            text = self.q

        return get_event_list(label=label, text=text)
