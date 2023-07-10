from django.views.generic.detail import DetailView
from gbe_utils.mixins import RoleRequiredMixin
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea
from gbetext import role_commit_map
from django.urls import reverse


class StaffAreaView(RoleRequiredMixin, DetailView):
    model = StaffArea
    context_object_name = 'area'
    template_name = 'gbe/report/staff_area_schedule.tmpl'
    view_permissions = ('Act Coordinator',
                        'Class Coordinator',
                        'Costume Coordinator',
                        'Vendor Coordinator',
                        'Volunteer Coordinator',
                        'Tech Crew',
                        'Scheduling Mavens',
                        'Staff Lead',
                        'Ticketing - Admin',
                        'Registrar',
                        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        other = "Potential"
        roles = []
        if 'filter' in list(self.request.GET.keys()) and (
                self.request.GET['filter'] == "Potential"):
            other = "Committed"
        for role, commit in list(role_commit_map.items()):
            if commit[0] == 1 or (
                    commit[0] > 0 and commit[0] < 4 and other == "Committed"):
                roles += [role]
        opps_response = None
        opps = None
        conference = None
        edit_link = None
        opps_response = get_occurrences(labels=[
            context['area'].conference.conference_slug,
            context['area'].slug])
        conference = context['area'].conference
        if context['area'].conference.status != 'completed':
            edit_link = reverse("edit_staff",
                                urlconf='gbe.scheduling.urls',
                                args=[context['area'].pk])
        if opps_response:
            show_general_status(self.request, opps_response, "staff_area")
            opps = opps_response.occurrences
        context.update({'opps': opps,
                        'conference': conference,
                        'role_commit_map': role_commit_map,
                        'visible_roles': roles,
                        'other_option': other,
                        'edit_link': edit_link})
        return context
