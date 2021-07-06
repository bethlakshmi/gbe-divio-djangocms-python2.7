from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib import messages
from gbe.models import UserMessage
from gbe_utils.text import no_permission_msg
from gbe.functions import validate_perms


class RoleRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        return validate_perms(self.request,
                              self.view_permissions,
                              require=False)

    def handle_no_permission(self):
        try:
            return super().handle_no_permission()
        except PermissionDenied:
            msg = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="NO_PERMISSION",
                    defaults={
                        'summary': "User doesn't have permission",
                        'description': no_permission_msg})
            messages.warning(self.request, msg[0].description)
            return HttpResponseRedirect(reverse('home', urlconf="gbe.urls"))
