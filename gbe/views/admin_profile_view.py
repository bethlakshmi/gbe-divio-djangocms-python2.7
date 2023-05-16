from django.shortcuts import get_object_or_404
from gbe.forms import ProfileAdminForm
from gbe.functions import validate_perms
from gbe.models import (
    UserMessage,
)
from gbe.models import Profile
from gbetext import admin_note
from gbe.views import EditProfileView


class AdminProfileView(EditProfileView):
    profile_form = ProfileAdminForm
    title = "Update User Profile"
    button = "Update User Account"
    header = "Update User's Profile"

    def groundwork(self, request, args, kwargs):
        admin_profile = validate_perms(
            request,
            ('Registrar', 'Act Coordinator', ))
        profile_id = kwargs.get("profile_id")

        self.profile = get_object_or_404(Profile, resourceitem_id=profile_id)
        admin_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="EDIT_PROFILE_NOTE",
            defaults={
                'summary': "Edit Profile Note",
                'description': admin_note})
        if self.profile.display_name.strip() != '':
            self.header = "Update %s's Profile" % self.profile.display_name
        return admin_message

    def get_user_success_message(self):
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="UPDATE_PROFILE",
            defaults={
                'summary': "Update Profile Success",
                'description': "Updated Profile"})
        message = "%s: %s" % (user_message[0].description,
                              str(self.profile))
        return message
