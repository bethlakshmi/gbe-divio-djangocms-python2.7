from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import (
    Profile,
    Troupe,
    UserMessage,
)
from gbe.functions import validate_perms
from settings import GBE_TABLE_FORMAT
from gbetext import profile_intro_msg


@login_required
@log_func
@never_cache
def ReviewProfilesView(request):
    admin_profile = validate_perms(request, ('Registrar',
                                             'Volunteer Coordinator',
                                             'Vendor Coordinator',
                                             'Scheduling Mavens',
                                             'Act Coordinator',
                                             'Class Coordinator',
                                             'Ticketing - Admin',
                                             'Staff Lead'))
    header = ['Name',
              'Username',
              'Last Login',
              'Contact Info',
              'Action']
    profiles = Profile.objects.filter(user_object__is_active=True)
    intro = UserMessage.objects.get_or_create(
        view="ReviewProfilesView",
        code="INTRODUCTION",
        defaults={
            'summary': "Top of Page Instructions",
            'description': profile_intro_msg})
    rows = []
    for aprofile in profiles:
        bid_row = {}
        last_login = "NEVER LOGGED IN"
        if aprofile.user_object.last_login:
            last_login = aprofile.user_object.last_login.strftime(
                GBE_TABLE_FORMAT)
        display_name = aprofile.display_name
        for troupe in Troupe.objects.filter(contact=aprofile):
            display_name += "<br>(%s)" % troupe.name
        bid_row['profile'] = (
            display_name,
            aprofile.user_object.username,
            last_login)
        bid_row['contact_info'] = {
            'contact_email': aprofile.user_object.email,
            'purchase_email': aprofile.purchase_email,
            'phone': aprofile.phone
        }
        bid_row['id'] = aprofile.resourceitem_id
        bid_row['actions'] = [
            {'url': reverse(
                'admin_landing_page',
                urlconf='gbe.urls',
                args=[aprofile.resourceitem_id]),
             'text': "View Landing Page"},
            {'url': reverse('welcome_letter',
                            urlconf='gbe.reporting.urls',
                            args=[aprofile.pk]),
             'text': "Welcome Letter"},
            {'url': reverse(
                'mail_to_individual',
                urlconf='gbe.email.urls',
                args=[aprofile.resourceitem_id]),
             'text': "Email"}
        ]
        if 'Registrar' in request.user.profile.privilege_groups:
            bid_row['actions'] += [
                {'url': "%s?next=%s" % (reverse(
                    'admin_profile',
                    urlconf='gbe.urls',
                    args=[aprofile.resourceitem_id]), request.path),
                 'text': "Update"}]
            bid_row['actions'] += [
                {'url': reverse('delete_profile',
                                urlconf='gbe.urls',
                                args=[aprofile.resourceitem_id]),
                 'text': "Delete"}]

        rows.append(bid_row)

    return render(request, 'gbe/profile_review.tmpl', {
      'columns': header,
      'rows': rows,
      'order': 0,
      'intro': intro[0].description})
