from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import Http404
from gbe_logging import log_func
from gbe.forms import (
    EmailPreferencesForm,
    EmailPreferencesNoLoginForm,
    SendEmailLinkForm,
)
from gbe.models import (
    Profile,
    ProfilePreferences,
    UserMessage,
)
from gbetext import (
    bad_token_msg,
    default_update_profile_msg,
    email_pref_note,
    link_sent_msg,
    send_link_message,
)
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from gbe.email.functions import (
    extract_email,
    send_unsubscribe_link,
)


class EditEmailView(View):
    title = "Update Email Preferences"
    button = "Update Settings"
    header = "Update Email Preferences"

    @method_decorator(csrf_exempt)
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

    def get_email_link(self, request, form=SendEmailLinkForm()):
        intro = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="SEND_LINK_NOTE",
            defaults={
                'summary': "Must Verify Email Note",
                'description': send_link_message})
        return render(request, 'gbe/update_email.tmpl',
                      {'form': form,
                       'title': "Unsubscribe from GBE Email",
                       'header': "Send Unsubscribe Link",
                       'button': "Send Link",
                       'email_note': intro[0].description})

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        if "token" in kwargs and kwargs.get("token") is not None:
            email = extract_email(kwargs.get("token"))
        else:
            self.token_parse_error(request)
            return self.get_email_link(request)
        if not email:
            self.token_parse_error(request)
            return self.get_email_link(request)
        try:
            profile = Profile.objects.get(
                user_object__email=email)
        except Profile.DoesNotExist:
            self.token_parse_error(request)
            return self.get_email_link(request)

        try:
            if len(profile.preferences.inform_about.strip()) > 0:
                inform_initial = eval(profile.preferences.inform_about)
        except ProfilePreferences.DoesNotExist:
            pref = ProfilePreferences(profile=profile)
            pref.save()

        email_focus = None
        email_initial = {'token': kwargs.get("token")}
        if 'email_disable' in request.GET:
            email_focus = str(request.GET['email_disable'])
            email_initial[email_focus] = False
        if 'interest_disable' in request.GET:
            interest_disable = eval(request.GET['interest_disable'])

        email_form = EmailPreferencesNoLoginForm(
            instance=profile.preferences,
            initial=email_initial,
            interest_disable=interest_disable)
        return render(request, 'gbe/update_email.tmpl',
                      {'email_form': email_form,
                       'email_note': self.get_intro()[0].description,
                       'email_focus': email_focus,
                       'title': self.title,
                       'view_title': "Email Options",
                       'button': self.button,
                       'header': self.header})

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        if 'email' in list(request.POST.keys()):
            form = SendEmailLinkForm(request.POST)
            if form.is_valid():
                try:
                    profile = Profile.objects.get(
                        user_object__email=form.cleaned_data["email"])
                    if profile.user_object.is_active:
                        send_unsubscribe_link(profile.user_object)
                except:
                    pass

                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SENT_EMAIL",
                    defaults={
                        'summary': "Sent Email with Link",
                        'description': link_sent_msg})
                messages.success(request, user_message[0].description)
                return self.success_redirect(request)
        else:
            form = EmailPreferencesNoLoginForm(request.POST)
            if form.is_valid():
                email = extract_email(form.cleaned_data["token"])
                if not email:
                    self.token_parse_error(request)
                    return self.get_email_link(request)
                try:
                    pref = ProfilePreferences.objects.get(
                        profile__user_object__email=email)
                    initated_email_form = EmailPreferencesForm(
                        request.POST,
                        instance=pref)
                    if not initated_email_form.is_valid():
                        raise Http404
                    initated_email_form.save(commit=True)
                except:
                    pass

                # if there is no user with this email, don't expose that, give
                # a positive either way
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="UPDATE_EMAIL",
                    defaults={
                        'summary': "Update Profile Success",
                        'description': default_update_profile_msg})
                messages.success(request, user_message[0].description)
                return self.success_redirect(request)
        return self.get_email_link(request, form)

    def token_parse_error(self, request):
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="BAD_TOKEN",
            defaults={
                'summary': "Unsubscribe Link Not Valid",
                'description': bad_token_msg})
        messages.error(request, user_message[0].description)

    def success_redirect(self, request):
        if request.user.is_authenticated:
            redirect_to = reverse('home', urlconf='gbe.urls')
        else:
            site = Site.objects.get_current()
            redirect_to = "http://%s" % site.domain
        return HttpResponseRedirect(redirect_to)
