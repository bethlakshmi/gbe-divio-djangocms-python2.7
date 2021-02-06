from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.forms import ConferenceStartChangeForm
from gbe.models import (
    Conference,
    ConferenceDay,
    UserMessage
)
from gbe.functions import validate_profile
from gbetext import (
    default_update_profile_msg,
    change_day_note,
)
from django.core.exceptions import PermissionDenied


class ManageConferenceView(View):
    title = "Manage Conference"
    button = "Change Dates"
    header = "Change Conference Start Day"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageConferenceView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_profile(request, require=False)
        if not self.profile.user_object.is_superuser:
            raise PermissionDenied
        message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="CHANGE_CONF_DAY_INTRO",
            defaults={
                'summary': "Change Conference Day Instructions",
                'description': change_day_note})
        return message[0].description

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
        forms = []
        for conference in Conference.objects.filter(
                status__in=('upcoming', 'ongoing')):
            first_day = ConferenceDay.objects.filter(
                conference=conference).order_by('day').first()
            forms += [(first_day,
                       ConferenceStartChangeForm(instance=first_day))]

        return render(request, 'gbe/manage_conference.tmpl',
                      {'forms': forms,
                       'intro': intro_message,
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
