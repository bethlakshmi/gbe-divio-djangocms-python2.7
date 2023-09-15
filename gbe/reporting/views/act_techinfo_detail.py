from django.views.generic.detail import DetailView
from django.core.exceptions import PermissionDenied
from gbe_utils.mixins import RoleRequiredMixin
from gbe.functions import validate_profile
from gbe.models import Act
from scheduler.idd import get_schedule
from gbe.scheduling.views.functions import show_general_status
from gbetext import acceptance_states


class ActTechInfoDetail(RoleRequiredMixin, DetailView):
    model = Act
    context_object_name = 'act'
    template_name = 'gbe/report/act_tech_detail.tmpl'
    view_permissions = ('Scheduling Mavens',
                        'Stage Manager',
                        'Tech Crew',
                        'Technical Director',
                        'Producer')

    def has_permission(self):
        role_permitted = super().has_permission()
        if not role_permitted:
            profile = validate_profile(self.request)
            if profile is not None:
                act = self.get_object()
                if profile in act.get_performer_profiles():
                    return True
        return role_permitted

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shows = []
        rehearsals = []
        order = -1
        role = "NO ROLE"

        if context['act'].accepted == 3:
            response = get_schedule(
                labels=[context['act'].b_conference.conference_slug],
                commitment=context['act'])
            show_general_status(self.request, response, "ActTechinfoDetail")
            for item in response.schedule_items:
                if item.event not in shows and (
                        item.event.event_style == 'Show'):
                    shows += [item.event]
                    order = item.commitment.order
                    role = item.commitment.role
                elif item.event not in rehearsals and (
                        item.event.event_style == 'Rehearsal Slot'):
                    rehearsals += [item.event]
        context.update({'state': acceptance_states[context['act'].accepted][1],
                        'shows': shows,
                        'order': order,
                        'role': role,
                        'rehearsals': rehearsals})
        return context
