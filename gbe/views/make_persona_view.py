from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from gbe.views import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from gbe.models import Persona
from gbe.forms import PersonaForm
from django.urls import reverse_lazy
from gbetext import default_edit_persona_msg


class PersonaCreate(CreatePopupMixin,
                    GbeFormMixin,
                    ProfileRequiredMixin,
                    CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    mode = "performer"
    valid_message = default_edit_persona_msg

    def get_initial(self):
        initial = super().get_initial()
        initial['performer_profile'] = self.request.user.profile
        initial['contact'] = self.request.user.profile
        return initial

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

class PersonaUpdate(UpdatePopupMixin,
                    GbeFormMixin,
                    ProfileRequiredMixin,
                    UpdateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    mode = "update"
    valid_message = default_edit_persona_msg

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)
