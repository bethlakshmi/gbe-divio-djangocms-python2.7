from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.forms import (
    EmailPreferencesForm,
    ParticipantForm,
    ProfilePreferencesForm,
)
from gbe.models import (
    Profile,
    ProfilePreferences,
    UserMessage
)
from gbe.functions import validate_profile
from gbetext import (
    default_update_profile_msg,
    email_pref_note,
)


class EditProfileView(View):
    profile_form = ParticipantForm
    title = "Update Your Profile"
    button = "Update My Account"
    header = "Update Your Profile"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditProfileView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_profile(request, require=False)
        if not self.profile:
            self.profile = Profile()
            self.profile.user_object = request.user
            self.profile.save()
            self.profile.preferences = ProfilePreferences()
            self.profile.preferences.save()
            self.profile.save()
        email_pref_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="EMAIL_PREF_NOTE",
            defaults={
                'summary': "Email Preference Settings Note",
                'description': email_pref_note})
        return email_pref_message

    def get_user_success_message(self):
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="UPDATE_PROFILE",
            defaults={
                'summary': "Update Profile Success",
                'description': default_update_profile_msg})
        return user_message[0].description

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        if self.profile.display_name.strip() == '':
            display_name = "%s %s" % (
                self.profile.user_object.first_name.strip(),
                self.profile.user_object.last_name.strip())
        else:
            display_name = self.profile.display_name
        if len(self.profile.how_heard.strip()) > 0:
            how_heard_initial = eval(self.profile.how_heard)
        else:
            how_heard_initial = []
        form = self.profile_form(instance=self.profile, initial={
            'email': self.profile.user_object.email,
            'first_name': self.profile.user_object.first_name,
            'last_name': self.profile.user_object.last_name,
            'display_name': display_name,
            'how_heard': how_heard_initial})
        inform_initial = []
        try:
            if len(self.profile.preferences.inform_about.strip()) > 0:
                inform_initial = eval(self.profile.preferences.inform_about)
        except ProfilePreferences.DoesNotExist:
            pref = ProfilePreferences(profile=self.profile)
            pref.save()

        prefs_form = ProfilePreferencesForm(prefix='prefs',
                                            instance=self.profile.preferences,
                                            initial={'inform_about':
                                                     inform_initial})
        email_focus = None
        email_form = EmailPreferencesForm(prefix='email_pref',
                                          instance=self.profile.preferences)
        return render(request, 'gbe/update_profile.tmpl',
                      {'left_forms': [form],
                       'right_forms': [prefs_form],
                       'email_form': email_form,
                       'email_note': intro_message[0].description,
                       'email_focus': email_focus,
                       'title': self.title,
                       'button': self.button,
                       'header': self.header})

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        form = self.profile_form(
            request.POST,
            instance=self.profile,
            initial={'email': self.profile.user_object.email})
        prefs_form = ProfilePreferencesForm(request.POST,
                                            instance=self.profile.preferences,
                                            prefix='prefs')
        email_form = EmailPreferencesForm(request.POST,
                                          instance=self.profile.preferences,
                                          prefix='email_pref')
        if form.is_valid() and prefs_form.is_valid() and email_form.is_valid():
            form.save(commit=True)
            if self.profile.purchase_email.strip() == '':
                self.profile.purchase_email = \
                    self.profile.user_object.email.strip()
            prefs_form.save(commit=True)
            email_form.save(commit=True)

            form.save()
            messages.success(request, self.get_user_success_message())
            if request.GET.get('next', None):
                redirect_to = request.GET['next']
            else:
                redirect_to = reverse('home', urlconf='gbe.urls')
            return HttpResponseRedirect(redirect_to)
        else:
            return render(
                request,
                'gbe/update_profile.tmpl',
                {'left_forms': [form],
                 'right_forms': [prefs_form],
                 'email_form': email_form,
                 'email_note': intro_message[0].description,
                 'title': self.title,
                 'button': self.button,
                 'header': self.header})
