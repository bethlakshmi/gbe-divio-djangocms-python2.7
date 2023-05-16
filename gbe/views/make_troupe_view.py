from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from gbe.models import (
    Profile,
    Troupe,
    UserMessage,
)
from gbe.forms import TroupeForm
from gbetext import (
    default_edit_troupe_msg,
    no_persona_msg,
    troupe_header_text,
)


class TroupeCreate(CreatePopupMixin,
                   GbeFormMixin,
                   ProfileRequiredMixin,
                   CreateView):
    model = Troupe
    form_class = TroupeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    intro_text = troupe_header_text
    mode = "troupe"
    valid_message = default_edit_troupe_msg

    def get_initial(self):
        initial = super().get_initial()
        initial['contact'] = self.request.user.profile
        initial['pronouns'] = "they/them"
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            resourceitem_id=self.request.user.profile.resourceitem_id)
        return form

    def get(self, request, *args, **kwargs):
        if self.request.user.profile.personae.all().count() == 0:
            msg = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="PERSONA_REQUIRED",
                defaults={
                    'summary': "Troupe requires Persona",
                    'description': no_persona_msg})
            messages.warning(self.request, msg[0].description)
            return redirect_to_login(
                self.request.path,
                reverse('persona-add', urlconf="gbe.urls", args=[1]),
                self.get_redirect_field_name())
        else:
            return super().get(request, *args, **kwargs)


class TroupeUpdate(UpdatePopupMixin,
                   GbeFormMixin,
                   ProfileRequiredMixin,
                   UpdateView):
    model = Troupe
    form_class = TroupeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'
    mode = "update"
    intro_text = troupe_header_text
    valid_message = default_edit_troupe_msg
    stay_here = True

    def get_initial(self):
        initial = super().get_initial()
        initial['pronouns'] = "they/them"
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            resourceitem_id=self.request.user.profile.resourceitem_id)
        return form

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse("performer-delete",
                                        urlconf="gbe.urls",
                                        args=[self.get_object().pk])
        return context
