from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool

from gbe.functions import validate_perms
from gbe.special_privileges import special_menu_tree

'''
  This is the best simulation of our old login menu I could come up with
  - the Django Menu doesn't offer Clickable top level menu items if there
  are children items.
'''


class LoginMenu(Menu):
    name = _("Dashboard")  # give the menu a name this is required.

    def get_nodes(self, request):
        """
        menus for all users or potential users to do account management
        """
        nodes = []

        nodes.append(NavigationNode(_("Dashboard"), "", 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Your Expo"),
                                    reverse('gbe:home'), 2, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Update Profile"),
                                    reverse('gbe:profile_update'), 3, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Change Password"),
                                    reverse('password_change'), 4, 1,
                                    attr={'visible_for_anonymous': False}))
        nodes.append(NavigationNode(_("Logout"),
                                    reverse('logout'), 5, 1,
                                    attr={'visible_for_anonymous': False}))
        return nodes

'''
  The special menu, I chose to separate them largely for modularity.
  Login and Special can all be in one function, but I thought the
  separation of areas was useful for readability.
'''


class SpecialMenu(Menu):
    name = _("Special")

    def get_nodes(self, request):
        """
        populate for users based on profile.
        Users must have special privileges to use this
        """
        nodes = []
        profile = validate_perms(request, 'any', require=False)
        if profile:
            privileges = set(request.user.profile.privilege_groups)
            roles = profile.get_roles()
            for role in ['Technical Director', 'Producer', 'Staff Lead']:
                if role in roles:
                    privileges.add(role)
            nodes.append(NavigationNode(_("Special"), "", 1))
            for node in special_menu_tree:
                if not privileges.isdisjoint(node['groups']):
                    nodes.append(NavigationNode(
                        title=node['title'],
                        url=node['url'],
                        id=node['id'],
                        parent_id=node['parent_id']))
        return nodes


menu_pool.register_menu(SpecialMenu)  # register the menu.
menu_pool.register_menu(LoginMenu)  # register the menu.
