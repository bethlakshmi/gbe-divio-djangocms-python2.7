from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from gbe.models import Performer
from gbe.forms import PersonaForm

class PerformerCreate(PermissionRequiredMixin, AccessMixin, CreateView):
    model = Performer
    form_class = PersonaForm
    template_name = 'gbe/modal_form.tmpl'

    def get_initial(self):
        initial = super().get_initial()
        initial['performer_profile'] = self.request.user.profile
        initial['contact'] = self.request.user.profile
        return initial

    def has_permission(self):
        return hasattr(self.request.user, 'profile')

class PerformerUpdate(PermissionRequiredMixin, UpdateView):
    model = Performer
    form_class = PersonaForm
