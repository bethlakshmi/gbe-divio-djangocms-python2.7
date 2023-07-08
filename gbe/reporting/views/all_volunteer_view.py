from gbe_utils.mixins import (
    ConferenceListView,
    RoleRequiredMixin,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea
from gbetext import role_commit_map
\

class AllVolunteerView(RoleRequiredMixin, ConferenceListView):
    model = StaffArea
    template_name = 'gbe/report/flat_volunteer_review.tmpl'
    view_permissions = 'any'


    def get_queryset(self):
        return self.model.objects.filter(conference=self.conference)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        roles = []
        for role, commit in list(role_commit_map.items()):
            if commit[0] > 0 and commit[0] < 4:
                roles += [role]

        opps_response = None
        opps = []
        opps_response = get_occurrences(
            labels=[self.conference.conference_slug, "Volunteer"])

        if opps_response:
            show_general_status(self.request, opps_response, "staff_area")
            for opp in opps_response.occurrences:
                item = {
                    'event': opp,
                    'areas': [],
                }
                for area in self.get_queryset().filter(slug__in=opp.labels):
                    item['areas'] += [area]
                opps += [item]
        context['opps'] = opps
        context['role_commit_map'] = role_commit_map
        context['visible_roles'] = roles
        context['columns'] = ['Event',
                               'Parent',
                               'Area',
                               'Location',
                               'Date/Time',
                               'Max',
                               'Current',
                               'Volunteers']
        return context
