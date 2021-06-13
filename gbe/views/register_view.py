from django.contrib.auth import (
    authenticate,
    login,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from gbe_logging import log_func
from gbe.forms import UserCreateForm
from gbetext import register_msg
from gbe.models import UserMessage


@log_func
def RegisterView(request):
    '''
    Allow a user to register with gbe. This should create both a user
    object and a profile. Currently, creates only the user object
    (profile produced by "update_profile")
    '''
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.clean_password2()
            form.save()
            user = authenticate(username=username,
                                password=password)
            login(request, user)
            if request.GET.get('next', None):
                return HttpResponseRedirect(
                    reverse(
                        'profile_update',
                        urlconf='gbe.urls') + '?next=' + request.GET['next'])

            return HttpResponseRedirect(reverse('profile_update',
                                                urlconf='gbe.urls'))
    else:
        form = UserCreateForm()
    return render(request, 'gbe/register.tmpl', {
        'form': form,
        'instructions': UserMessage.objects.get_or_create(
            view="RegisterView",
            code="REGISTRATION_INSTRUCTIONS",
            defaults={
                'summary': "Instructions for Registration",
                'description': register_msg})[0].description})
