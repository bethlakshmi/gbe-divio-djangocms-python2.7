from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
from gbe_utils.mixins import (
    GbeContextMixin,
    RoleRequiredMixin,
)
from gbe.models import (
    Profile,
    ProfilePreferences,
    UserMessage,
)
from gbe.forms import (
    EmailPreferencesForm,
    ProfileAdminForm,
    ProfilePreferencesForm,
)
from gbetext import (
    merge_profile_msg,
    warn_user_merge_delete,
)


class MergeProfileData(GbeContextMixin, RoleRequiredMixin, UpdateView):
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

        if self.request.user == context['otherprofile'].user_object:
            warning = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SELF_MERGE_WARNING",
                defaults={
                    'summary': "Warning when merge deletes current account",
                    'description': warn_user_merge_delete})[0].description
            messages.warning(
                self.request,
                warning)

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
        display_name = self.object.display_name
        purchase_email = self.object.purchase_email
        how_heard_initial = []
        if self.object.display_name.strip() == '':
            display_name = "%s %s" % (
                self.object.user_object.first_name.strip(),
                self.object.user_object.last_name.strip())

        if len(self.object.how_heard.strip()) > 0:
            how_heard_initial = eval(self.object.how_heard)

        if self.object.purchase_email.strip() == '':
            purchase_email = self.object.user_object.email

        return {'email': self.object.user_object.email,
                'first_name': self.object.user_object.first_name,
                'last_name': self.object.user_object.last_name,
                'display_name': display_name,
                'purchase_email': purchase_email,
                'how_heard': how_heard_initial}
