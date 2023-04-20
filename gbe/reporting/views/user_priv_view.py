from django.views.generic.list import ListView
from gbe_utils.mixins import GbeContextMixin
from django.contrib.auth.models import (
    Group,
    User,
)
from django.db.models import Q
from gbe.functions import (
    get_current_conference,
)
from gbetext import privileged_event_roles


class UserPrivView(GbeContextMixin, ListView):
    model = User
    template_name = 'gbe/report/user_priv.tmpl'
    queryset = User.objects.exclude(groups=None)
    page_title = 'User Privilege Report'
    view_title = 'Users with Special Privileges'
    intro_text = 'This is all users that currently have privileges in the site.'

    def get_context_data(self, **kwargs):
        from gbe.special_privileges import special_menu_tree
        context = super().get_context_data(**kwargs)
        context['columns'] = ['User',
                              'Last Login',
                              'Permanent Groups',
                              'Conference Groups',
                              'Action']
        group_power = {}
        for group in Group.objects.all():
            group_power[group.name] = {}
        for role in privileged_event_roles:
            group_power[role] = {}

        for node in special_menu_tree:
            for group in node['groups']:
                if node['parent_id'] == 1:
                    group_power[group][node['id']] = {
                        'children': [],
                        'title': node['title'],
                    }
                else:
                    if node['parent_id'] in group_power[group].keys():
                        group_power[group][
                            node['parent_id']]['children'] += [node['title']]
                    else:
                        raise Exception(
                            "menu: %s, group: %s - parent not found" % (
                                node['title'],
                                group))
        context['group_power'] = group_power
        return context
