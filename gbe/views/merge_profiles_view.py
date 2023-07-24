from django.views.generic import (
    FormView,
    UpdateView,
)
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
    BidBioMergeForm,
    EmailPreferencesForm,
    ProfileAdminForm,
    ProfilePreferencesForm,
)
from gbetext import (
    merge_bio_msg,
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
    form_class = ProfileAdminForm
    view_permissions = ('Registrar', )
    intro_text = merge_profile_msg
    page_title = 'Merge Users - Verify Info'
    view_title = 'Merge Users - Verify Info'
    template_name = 'gbe/profile_merge.tmpl'
    context_object_name = 'target'


    def form_valid(self, form):
        response = super().form_valid(form)
        prefs_form = ProfilePreferencesForm(self.request.POST,
                                            instance=self.object.preferences,
                                            prefix='prefs')
        email_form = EmailPreferencesForm(self.request.POST,
                                          instance=self.object.preferences,
                                          prefix='email_pref')
        if form.is_valid() and prefs_form.is_valid() and email_form.is_valid():
            if self.object.purchase_email.strip() == '':
                self.object.purchase_email = \
                    self.object.user_object.email.strip()
            prefs_form.save(commit=True)
            email_form.save(commit=True)
        else:
            # TODO - should I handle differently
            raise Exception("something has gone very odd, contact the admin")
        return response


    def get_success_url(self):
        return reverse("merge_bios", urlconf="gbe.urls", args=[
            self.object.pk,
            self.kwargs['from_pk']])

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

class MergeBios(GbeContextMixin, RoleRequiredMixin, FormView):
    success_url = reverse_lazy("manage_users", urlconf="gbe.urls")
    form_class = BidBioMergeForm
    view_permissions = ('Registrar', )
    intro_text = merge_bio_msg
    page_title = 'Merge Users - Merge Bios'
    view_title = 'Merge Users - Merge Bios'
    template_name = 'gbe/bid_bio_merge.tmpl'

    def get_initial(self):
        self.otherprofile = get_object_or_404(Profile,
                                              pk=self.kwargs['from_pk'])
        self.targetprofile = get_object_or_404(Profile,
                                               pk=self.kwargs['pk'])
        return {
            'otherprofile': self.otherprofile,
            'targetprofile': self.targetprofile,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorting_off'] = True
        context['columns'] = ['Value',
                              'Target',
                              'To be Merged',
                              'Fix it Here']
        context['otherprofile'] = self.otherprofile 
        context['targetprofile'] = self.targetprofile
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        for bio in self.otherprofile .bio_set.all():
            if form.cleaned_data['bio_%d' % bio.pk] == '':
                print("merge it")
            else:
                print("merge bids to %s" % str(Bio.objects.get(
                    pk=form.cleaned_data['bio_%d' % bio.pk])))
        return response
