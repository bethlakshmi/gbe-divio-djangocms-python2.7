from django.views.generic import CreateView
from django.contrib.auth import (
    authenticate,
    login,
)
from django.urls import reverse_lazy
from django.shortcuts import redirect
from gbe.forms import UserCreateForm
from gbetext import register_msg
from gbe.models import (
    Profile,
    ProfilePreferences,
)
from gbe_utils.mixins import SubwayMapMixin


class RegisterView(SubwayMapMixin, CreateView):

    form_class = UserCreateForm
    template_name = 'gbe/register.tmpl'
    success_url = reverse_lazy('profile_update', urlconf='gbe.urls')
    intro_text = register_msg
    page_title = 'Register For An Account'
    view_title = 'Create an Account'

    def form_valid(self, form):
        super().form_valid(form)
        username = form.cleaned_data['email']
        password = form.clean_password2()
        user = authenticate(username=username,
                            password=password)
        profile = Profile(user_object=user,
                          display_name=form.cleaned_data['name'])
        profile.save()
        profile.preferences = ProfilePreferences()
        profile.preferences.save()
        profile.save()
        login(self.request, user)
        return redirect(self.get_success_url())
