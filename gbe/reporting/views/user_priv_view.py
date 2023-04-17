from django.views.generic.list import ListView
from gbe_utils.mixins import GbeContextMixin
from django.contrib.auth.models import User
from django.db.models import Q
from gbe.functions import (
    get_current_conference,
)
from scheduler.idd import get_people


class UserPrivView(GbeContextMixin, ListView):
    model = User
    template_name = 'gbe/report/user_priv.tmpl'
    queryset = User.objects.exclude(groups=None)
    page_title = 'User Privilege Report'
    view_title = 'Users with Special Privileges'
    intro_text = 'This is all users that currently have privileges in the site.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = ['User',
                              'Last Login',
                              'Permanent Groups',
                              'Conference Groups',
                              'Action']
        return context
