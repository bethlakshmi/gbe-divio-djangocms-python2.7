from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from gbe_logging import log_func
from gbe.forms import (
    ProfileAdminForm,
    ProfilePreferencesForm,
)
from gbe.functions import validate_perms
from gbe.models import Profile


@login_required
@log_func
@never_cache
def AdminProfileView(request, profile_id):
    admin_profile = validate_perms(request, ('Registrar',))
    user_profile = get_object_or_404(Profile, resourceitem_id=profile_id)

    if request.method == 'POST':
        form = ProfileAdminForm(
            request.POST,
            instance=user_profile,
            initial={'email': user_profile.user_object.email}
        )
        prefs_form = ProfilePreferencesForm(request.POST,
                                            instance=user_profile.preferences,
                                            prefix='prefs')

        if form.is_valid():
            form.save(commit=True)
            if prefs_form.is_valid():
                prefs_form.save(commit=True)
                user_profile.preferences = prefs_form.save()
            user_profile.save()

            form.save()
            return HttpResponseRedirect(reverse('manage_users',
                                                urlconf='gbe.urls'))
        else:
            return render(request, 'gbe/update_profile.tmpl',
                          {'left_forms': [form], 'right_forms': [prefs_form]})

    else:
        if user_profile.display_name.strip() == '':
            display_name = "%s %s" % (user_profile.user_object.first_name,
                                      user_profile.user_object.last_name)
        else:
            display_name = user_profile.display_name
        if len(user_profile.how_heard.strip()) > 0:
            how_heard_initial = eval(user_profile.how_heard)
        else:
            how_heard_initial = []

        form = ProfileAdminForm(
            instance=user_profile,
            initial={'email': user_profile.user_object.email,
                     'first_name': user_profile.user_object.first_name,
                     'last_name': user_profile.user_object.last_name,
                     'display_name': display_name,
                     'how_heard': how_heard_initial})

        if len(user_profile.preferences.inform_about.strip()) > 0:
            inform_initial = eval(user_profile.preferences.inform_about)
        else:
            inform_initial = []
        prefs_form = ProfilePreferencesForm(prefix='prefs',
                                            instance=user_profile.preferences,
                                            initial={'inform_about':
                                                     inform_initial})
        return render(request,
                      'gbe/update_profile.tmpl',
                      {'left_forms': [form],
                       'right_forms': [prefs_form],
                       'display_name': user_profile.display_name})
