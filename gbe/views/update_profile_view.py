from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse
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


@login_required
@log_func
@never_cache
def UpdateProfileView(request):
    profile = validate_profile(request, require=False)
    if not profile:
        profile = Profile()
        profile.user_object = request.user
        profile.save()
        profile.preferences = ProfilePreferences()
        profile.preferences.save()
        profile.save()

    email_pref_message = UserMessage.objects.get_or_create(
        view="UpdateProfileView",
        code="EMAIL_PREF_NOTE",
        defaults={
            'summary': "Email Preference Settings Note",
            'description': email_pref_note})
    if request.method == 'POST':
        form = ParticipantForm(request.POST,
                               instance=profile,
                               initial={'email': profile.user_object.email
                                        })
        prefs_form = ProfilePreferencesForm(request.POST,
                                            instance=profile.preferences,
                                            prefix='prefs')
        email_form = EmailPreferencesForm(request.POST,
                                          instance=profile.preferences,
                                          prefix='email_pref')
        if form.is_valid() and prefs_form.is_valid() and email_form.is_valid():
            form.save(commit=True)
            if profile.purchase_email.strip() == '':
                profile.purchase_email = request.user.email.strip()
            prefs_form.save(commit=True)
            email_form.save(commit=True)

            form.save()
            user_message = UserMessage.objects.get_or_create(
                view='UpdateProfileView',
                code="UPDATE_PROFILE",
                defaults={
                    'summary': "Update Profile Success",
                    'description': default_update_profile_msg})
            messages.success(request, user_message[0].description)
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
                 'email_note': email_pref_message[0].description})

    else:
        if profile.display_name.strip() == '':
            display_name = "%s %s" % (request.user.first_name.strip(),
                                      request.user.last_name.strip())
        else:
            display_name = profile.display_name
        if len(profile.how_heard.strip()) > 0:
            how_heard_initial = eval(profile.how_heard)
        else:
            how_heard_initial = []
        form = ParticipantForm(instance=profile,
                               initial={'email': request.user.email,
                                        'first_name': request.user.first_name,
                                        'last_name': request.user.last_name,
                                        'display_name': display_name,
                                        'how_heard': how_heard_initial})
        inform_initial = []
        try:
            if len(profile.preferences.inform_about.strip()) > 0:
                inform_initial = eval(profile.preferences.inform_about)
        except ProfilePreferences.DoesNotExist:
            pref = ProfilePreferences(profile=profile)
            pref.save()

        prefs_form = ProfilePreferencesForm(prefix='prefs',
                                            instance=profile.preferences,
                                            initial={'inform_about':
                                                     inform_initial})
        email_focus = None
        email_initial = {}
        if 'email_disable' in request.GET:
            email_focus = str(request.GET['email_disable'])
            email_initial = {
                email_focus: False,
            }
        email_form = EmailPreferencesForm(prefix='email_pref',
                                          instance=profile.preferences,
                                          initial=email_initial)
        return render(request, 'gbe/update_profile.tmpl',
                      {'left_forms': [form],
                       'right_forms': [prefs_form],
                       'email_form': email_form,
                       'email_note': email_pref_message[0].description,
                       'email_focus': email_focus})
