from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from gbe.views import ProfileRequiredMixin
from django_addanother.views import CreatePopupMixin
from gbe.models import Persona
from gbe.forms import PersonaForm
from django.urls import reverse_lazy


class PersonaCreate(CreatePopupMixin, ProfileRequiredMixin, CreateView):
    model = Persona
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        context['mode'] = "performer"
        return context

class PersonaUpdate(CreatePopupMixin, ProfileRequiredMixin, UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        context['mode'] = "update"
        return context

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)
