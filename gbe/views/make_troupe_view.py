from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django_addanother.views import CreatePopupMixin
from django.urls import reverse_lazy
from django.contrib import messages
from gbe.views import ProfileRequiredMixin
from gbe.models import (
    Profile,
    Troupe,
)
from gbe.forms import TroupeForm


class TroupeCreate(CreatePopupMixin, ProfileRequiredMixin, CreateView):
    model = Troupe
    form_class = TroupeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'

    def get_initial(self):
        initial = super().get_initial()
        initial['contact'] = self.request.user.profile
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        context['mode'] = "troupe"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            resourceitem_id=self.request.user.profile.resourceitem_id)
        return form


class TroupeUpdate(CreatePopupMixin, ProfileRequiredMixin, UpdateView):
    model = Troupe
    form_class = TroupeForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('home', urlconf="gbe.urls")
    page_title = 'Manage Troupe'
    view_title = 'Tell Us About Your Troupe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['view_title'] = self.view_title
        context['mode'] = "update"
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            resourceitem_id=self.request.user.profile.resourceitem_id)
        return form

    def get_queryset(self):
        return self.model.objects.filter(
            contact__user_object=self.request.user)
