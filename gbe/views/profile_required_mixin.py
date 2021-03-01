from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib import messages
from gbe.models import UserMessage
from gbetext import no_profile_msg


class ProfileRequiredMixin(PermissionRequiredMixin):
    def has_permission(self):
        return hasattr(self.request.user,
                       'profile') and self.request.user.profile.complete

    def handle_no_permission(self):
        try:
            return super().handle_no_permission()
        except PermissionDenied:
            msg = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="PROFILE_INCOMPLETE",
                    defaults={
                        'summary': "Profile Incomplete",
                        'description': no_profile_msg})
            messages.warning(self.request, msg[0].description)
            return redirect_to_login(
                self.request.build_absolute_uri(),
                reverse('profile_update', urlconf="gbe.urls"),
                self.get_redirect_field_name())
