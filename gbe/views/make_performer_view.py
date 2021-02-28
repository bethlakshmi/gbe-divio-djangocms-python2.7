from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import (
    AccessMixin,
    PermissionRequiredMixin,
)
from django_addanother.views import CreatePopupMixin
from gbe.models import Performer
from gbe.forms import PersonaForm
from django.urls import reverse_lazy


class PerformerCreate(CreatePopupMixin, PermissionRequiredMixin, CreateView):
    model = Performer
    form_class = PersonaForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'

    def get_initial(self):
        initial = super().get_initial()
        initial['performer_profile'] = self.request.user.profile
        initial['contact'] = self.request.user.profile
        return initial

    def has_permission(self):
        return hasattr(self.request.user, 'profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        context['mode'] = "performer"
        return context

class PerformerUpdate(PermissionRequiredMixin, UpdateView):
    model = Performer
    form_class = PersonaForm
