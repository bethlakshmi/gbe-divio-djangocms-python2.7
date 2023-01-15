from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
    SubwayMapMixin,
)
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from gbe.models import Persona
from gbe.forms import PersonaForm
from django.urls import reverse, reverse_lazy
from gbetext import (
    default_create_persona_msg,
    default_edit_persona_msg,
)


class PersonaCreate(CreatePopupMixin,
                    SubwayMapMixin,
                    ProfileRequiredMixin,
                    CreateView):
    model = Persona
    form_class = PersonaForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Stage Persona'
    view_title = 'Tell Us About Your Stage Persona'
    mode = "performer"
    valid_message = default_create_persona_msg
    social_links = True

    def get_initial(self):
        initial = super().get_initial()
        initial['performer_profile'] = self.request.user.profile
        initial['contact'] = self.request.user.profile
        return initial


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
    social_links = True

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse("performer-delete",
                                        urlconf="gbe.urls",
                                        args=[self.get_object().pk])
        return context
