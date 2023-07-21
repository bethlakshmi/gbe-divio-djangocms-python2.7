from django.views.generic import UpdateView
from gbe.views import ReviewProfilesView
from gbe.functions import validate_perms
from django.shortcuts import get_object_or_404
from django.urls import (
    reverse,
    reverse_lazy,
)
from gbe_utils.mixins import (
    GbeContextMixin,
    RoleRequiredMixin,
)
from gbe.models import (
    Bio,
    Profile,
    ProfilePreferences,
    UserMessage,
)
from gbe.forms import (
    EmailPreferencesForm,
    ParticipantForm,
    ProfilePreferencesForm,
)
from gbetext import (
    merge_profile_msg,
    merge_users_msg,
)


class MergeProfileSelect(ReviewProfilesView):
    page_title = 'Merge Users'
    view_title = 'Merge Users'
    intro_text = merge_users_msg
    view_permissions = ('Registrar', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(pk=self.kwargs['pk'])

    def set_actions(self, profile):
        return [{'url': reverse('merge_profiles',
                                urlconf='gbe.urls',
                                args=[self.kwargs['pk'], profile.pk]),
                 'text': "Merge Second"}]


class MergeProfiles(GbeContextMixin, RoleRequiredMixin, UpdateView):
    model = Profile
    success_url = reverse_lazy("manage_users", urlconf="gbe.urls")
    form_class = ParticipantForm
    view_permissions = ('Registrar', )
    intro_text = merge_profile_msg
    page_title = 'Merge Users - Verify Info'
    view_title = 'Merge Users - Verify Info'
    template_name = 'gbe/profile_merge.tmpl'
    context_object_name = 'target'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorting_off'] = True
        context['columns'] = ['Value',
                              'Target',
                              'To be Merged',
                              'Fix it Here']
        context['otherprofile'] = get_object_or_404(Profile,
                                                    pk=self.kwargs['from_pk'])
        inform_initial = []
        try:
            if len(self.object.preferences.inform_about.strip()) > 0:
                inform_initial = eval(self.object.preferences.inform_about)
        except ProfilePreferences.DoesNotExist:
            pref = ProfilePreferences(profile=self.object)
            pref.save()
        context['prefs_form'] = ProfilePreferencesForm(
            prefix='prefs',
            instance=self.object.preferences,
            initial={'inform_about': inform_initial})
        context['email_form'] = EmailPreferencesForm(
            prefix='email_pref',
            label_suffix="",
            instance=self.object.preferences)
        return context

    def get_initial(self):
        display_name = ""
        how_heard_initial = []
        if self.object.display_name.strip() == '':
            display_name = "%s %s" % (
                self.object.user_object.first_name.strip(),
                self.object.user_object.last_name.strip())
        else:
            display_name = self.object.display_name
        if len(self.object.how_heard.strip()) > 0:
            how_heard_initial = eval(self.object.how_heard)

        return {'email': self.object.user_object.email,
                'first_name': self.object.user_object.first_name,
                'last_name': self.object.user_object.last_name,
                'display_name': display_name,
                'how_heard': how_heard_initial}
