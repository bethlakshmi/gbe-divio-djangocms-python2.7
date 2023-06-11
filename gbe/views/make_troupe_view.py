from django.contrib.auth.models import User
from django.views.generic.edit import (
    CreateView,
    UpdateView,
)
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from gbe_utils.mixins import (
    GbeFormMixin,
    ProfileRequiredMixin,
)
from gbe.models import (
    Bio,
    Profile,
)
from gbe.forms import TroupeForm
from gbetext import (
    default_edit_troupe_msg,
    troupe_header_text,
)
from scheduler.idd import (
    create_bookable_people,
    get_bookable_people,
    update_bookable_people,
)
from gbe.scheduling.views.functions import show_general_status


class TroupeCreate(CreatePopupMixin,
                   GbeFormMixin,
                   ProfileRequiredMixin,
                   CreateView):
    model = Bio
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
        initial['multiple_performers'] = True
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            pk=self.request.user.profile.pk)
        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        users = User.objects.filter(
            profile__in=form.cleaned_data['membership'])
        idd_resp = create_bookable_people(self.object, users)
        show_general_status(self.request, idd_resp, self.__class__.__name__)
        return response


class TroupeUpdate(UpdatePopupMixin,
                   GbeFormMixin,
                   ProfileRequiredMixin,
                   UpdateView):
    model = Bio
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
        response = get_bookable_people(self.object.pk,
                                       self.object.__class__.__name__)
        show_general_status(self.request, response, self.__class__.__name__)
        initial['membership'] = Profile.objects.filter(
            user_object__in=response.people[0].users)
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['contact'].queryset = Profile.objects.filter(
            pk=self.request.user.profile.pk)
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

    def form_valid(self, form):
        response = super().form_valid(form)
        users = User.objects.filter(
            profile__in=form.cleaned_data['membership'])
        idd_resp = update_bookable_people(self.object, users)
        show_general_status(self.request, idd_resp, self.__class__.__name__)
        return response
