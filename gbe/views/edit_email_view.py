from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import Http404
from gbe_logging import log_func
from gbe.forms import EmailPreferencesForm
from gbe.models import (
    Profile,
    ProfilePreferences,
    UserMessage
)
from gbetext import (
    default_update_profile_msg,
    email_pref_note,
)
from django.views.decorators.csrf import csrf_exempt


class EditEmailView(View):
    title = "Update Your Email Preferences"
    button = "Update My Account"
    header = "Update Your Email Preferences"

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(EditEmailView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        if "email" in kwargs:
            self.profile = Profile.objects.get(
                user_object__email=kwargs.get("email"))
        else:
            raise Http404
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
            code="UPDATE_EMAIL",
            defaults={
                'summary': "Update Profile Success",
                'description': default_update_profile_msg})
        return user_message[0].description

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        inform_initial = []
        try:
            if len(self.profile.preferences.inform_about.strip()) > 0:
                inform_initial = eval(self.profile.preferences.inform_about)
        except ProfilePreferences.DoesNotExist:
            pref = ProfilePreferences(profile=self.profile)
            pref.save()

        email_focus = None
        email_initial = {}
        if 'email_disable' in request.GET:
            email_focus = str(request.GET['email_disable'])
            email_initial = {
                email_focus: False,
            }
        email_form = EmailPreferencesForm(prefix='email_pref',
                                          instance=self.profile.preferences,
                                          initial=email_initial)
        return render(request, 'gbe/update_email.tmpl',
                      {'email_form': email_form,
                       'email_note': intro_message[0].description,
                       'email_focus': email_focus,
                       'title': self.title,
                       'button': self.button,
                       'header': self.header})

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        email_form = EmailPreferencesForm(request.POST,
                                          instance=self.profile.preferences,
                                          prefix='email_pref')

        if email_form.is_valid():
            email_form.save(commit=True)
            messages.success(request, self.get_user_success_message())
            messages.success(request, self.get_user_success_message())
            if request.user.is_authenticated:
                redirect_to = reverse('home', urlconf='gbe.urls')
            else:
                redirect_to = "/"

            return HttpResponseRedirect(redirect_to)
        else:
            return render(
                request,
                'gbe/update_email.tmpl',
                {'email_form': email_form,
                 'email_note': intro_message[0].description,
                 'title': self.title,
                 'button': self.button,
                 'header': self.header})
