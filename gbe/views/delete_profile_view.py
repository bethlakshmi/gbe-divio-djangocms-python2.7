from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import (
    Profile,
    UserMessage,
)
from scheduler.models import ResourceAllocation
from gbe.functions import validate_perms
from gbetext import (
    default_deactivate_profile_admin_msg,
    default_delete_profile_admin_msg,
)
from django.shortcuts import get_object_or_404


@login_required
@log_func
@never_cache
def DeleteProfileView(request, profile_id):
    admin_profile = validate_perms(request, ('Registrar',))
    if profile_id:
        user_profile = get_object_or_404(Profile, resourceitem_id=profile_id)
    return_page = HttpResponseRedirect(reverse('manage_users',
                                               urlconf='gbe.urls'))

    bookings = ResourceAllocation.objects.filter(
        resource__worker___item=user_profile).count()
    if (bookings >= 1) or (
            user_profile.personae.count() >= 1) or (
            user_profile.contact.count() >= 1) or (
            user_profile.volunteering.count() >= 1) or (
            user_profile.costumes.count() >= 1) or (
            user_profile.vendor_set.count() >= 1) or (
            user_profile.bidevaluation_set.count() >= 1) or (
            user_profile.actbidevaluation_set.count() >= 1) or (
            user_profile.user_object.purchaser_set.count() >= 1):
        user_profile.user_object.is_active = False
        user_profile.user_object.save()
        admin_page = "<a href='/admin/auth/user/%d/'>User Page</a>" % (
            user_profile.user_object.pk
        )
        user_message = UserMessage.objects.get_or_create(
            view='DeleteProfileView',
            code="DEACTIVATE_PROFILE_ADMIN",
            defaults={
                'summary': "Update Profile Success",
                'description':
                    default_deactivate_profile_admin_msg + admin_page
                })
    else:
        user_profile.user_object.delete()
        user_message = UserMessage.objects.get_or_create(
            view='DeleteProfileView',
            code="DELETE_PROFILE_ADMIN",
            defaults={
                'summary': "Update Profile Success",
                'description': default_delete_profile_admin_msg})
    deletion_summary = "Removed %s<br><br>\n%s" % (
        user_profile.user_object.username,
        user_message[0].description)
    messages.success(request, deletion_summary)
    return return_page
