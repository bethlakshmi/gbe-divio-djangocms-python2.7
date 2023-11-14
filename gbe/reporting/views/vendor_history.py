from gbe_utils.mixins import RoleRequiredMixin
from django.views.generic.list import ListView
from gbe.models import Business


class VendorHistory(RoleRequiredMixin, ListView):
    model = Business
    context_object_name = "businesses"
    template_name = 'gbe/report/vendor_history.tmpl'
    view_permissions = ['Vendor Coordinator']
    title = "Volunteers Over Time"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        context['columns'] = ['Business',
                              'Conferences Attended',
                              'Address',
                              'Description',
                              'Contact']
        return context
