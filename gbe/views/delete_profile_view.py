from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import (
    Act,
    Class,
    Profile,
    UserMessage,
    Vendor,
)
from gbe.functions import validate_perms
from gbetext import (
    default_deactivate_profile_admin_msg,
    default_delete_profile_admin_msg,
)
from django.shortcuts import get_object_or_404
from scheduler.idd import (
    delete_bookable_people,
    get_schedule,
)
from gbe.scheduling.views.functions import show_general_status


@login_required
@log_func
@never_cache
def DeleteProfileView(request, profile_id):
    troupe_is_booked = False
    admin_profile = validate_perms(request, ('Registrar',))
    user_profile = get_object_or_404(Profile, pk=profile_id)
    return_page = HttpResponseRedirect(
        request.GET.get('next', reverse('manage_users', urlconf='gbe.urls')))

    response = get_schedule(user=user_profile.user_object)
    show_general_status(request,
                        response,
                        DeleteProfileView.__class__.__name__)

    for troupe in user_profile.bio_set.filter(multiple_performers=True):
        troupe_response = get_schedule(public_class=troupe.__class__.__name__,
                                       public_id=troupe.pk)
        if len(troupe_response.schedule_items) >= 1:
            troupe_is_booked = True

    show_general_status(request,
                        response,
                        DeleteProfileView.__class__.__name__)

    vendor_bids = Vendor.objects.filter(business__owners=user_profile)
    acts = Act.objects.filter(bio__contact=user_profile)
    classes = Class.objects.filter(teacher_bio__contact=user_profile)
    if troupe_is_booked or (len(response.schedule_items) >= 1) or (
            classes.count() >= 1) or (vendor_bids.count() >= 1) or (
            user_profile.volunteering.count() >= 1) or (
            user_profile.costumes.count() >= 1) or (acts.count() >= 1) or (
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
        # if person is not found, it's OK
        for bio in user_profile.bio_set.all():
            delete_bookable_people(bio)
            bio.delete()
        delete_bookable_people(user_profile)
        user_profile.user_object.delete()
        user_message = UserMessage.objects.get_or_create(
            view='DeleteProfileView',
            code="DELETE_PROFILE_ADMIN",
            defaults={
                'summary': "Delete Profile Success",
                'description': default_delete_profile_admin_msg})
    deletion_summary = "Removed %s<br><br>\n%s" % (
        user_profile.user_object.username,
        user_message[0].description)
    messages.success(request, deletion_summary)
    return return_page
