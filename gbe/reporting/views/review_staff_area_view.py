from gbe_utils.mixins import (
    ConferenceListView,
    RoleRequiredMixin,
)
from gbe.models import StaffArea


class ReviewStaffAreaarView(RoleRequiredMixin, ConferenceListView):
    model = StaffArea
    context_object_name = "areas"
    template_name = 'gbe/report/staff_areas.tmpl'
    view_permissions = 'any'

    def get_queryset(self):
        return self.model.objects.filter(conference=self.conference)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = ['Area', 'Leaders', 'Check Staffing']
        return context
