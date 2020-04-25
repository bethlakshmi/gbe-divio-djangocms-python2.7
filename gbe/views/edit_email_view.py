from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import Http404
from gbe_logging import log_func
from gbe.forms import (
    EmailPreferencesForm,
    EmailPreferencesNoLoginForm,
)
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
    profile = None

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(EditEmailView, self).dispatch(*args, **kwargs)

    def get_intro(self):
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
        email_focus = None
        email_initial = {}
        if 'email_disable' in request.GET:
            email_focus = str(request.GET['email_disable'])
            email_initial = {email_focus: False}

        email_form = EmailPreferencesNoLoginForm(initial=email_initial)
        return render(request, 'gbe/update_email.tmpl',
                      {'email_form': email_form,
                       'email_note': self.get_intro()[0].description,
                       'email_focus': email_focus,
                       'title': self.title,
                       'button': self.button,
                       'header': self.header})

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        email_form = EmailPreferencesNoLoginForm(request.POST)

        if email_form.is_valid():
            profile = Profile.objects.get(
                user_object__email=email_form.cleaned_data['email'])
            try:
                initated_email_form = EmailPreferencesForm(
                    request.POST,
                    instance=profile.preferences)
            except:
                pref = ProfilePreferences(profile=self.profile)
                pref.save()
                initated_email_form = EmailPreferencesForm(
                    request.POST,
                    instance=pref)

            if not initated_email_form.is_valid():
                raise Http404
            initated_email_form.save(commit=True)
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
                 'email_note': self.get_intro()[0].description,
                 'title': self.title,
                 'button': self.button,
                 'header': self.header})
