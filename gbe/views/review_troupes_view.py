from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import Troupe
from gbe.functions import validate_perms


@login_required
@log_func
@never_cache
def ReviewTroupesView(request):
    admin_profile = validate_perms(request, ('Registrar',
                                             'Volunteer Coordinator',
                                             'Vendor Coordinator',
                                             'Scheduling Mavens',
                                             'Act Coordinator',
                                             'Class Coordinator',
                                             'Ticketing - Admin',
                                             'Staff Lead'))
    header = ['Troupe',
              'Contact',
              'Members',
              'Action']
    troupes = Troupe.objects.filter(contact__user_object__is_active=True)
    rows = []
    for troupe in troupes:
        bid_row = {}
        members = ""
        for member in troupe.membership.all():
            members += "%s,<br>" % member.name
        bid_row['profile'] = (
            troupe.name,
            "%s<br>%s" % (troupe.contact.display_name,
                          troupe.contact.user_object.email),
            members)
        bid_row['id'] = troupe.resourceitem_id
        bid_row['actions'] = [
            {'url': reverse(
                'admin_landing_page',
                urlconf='gbe.urls',
                args=[troupe.contact.resourceitem_id]),
             'text': "View Landing Page"},
            {'url': reverse(
                'mail_to_individual',
                urlconf='gbe.email.urls',
                args=[troupe.contact.resourceitem_id]),
             'text': "Email"}
        ]
        if 'Registrar' in request.user.profile.privilege_groups:
            bid_row['actions'] += [
                {'url': "%s?next=%s" % (reverse(
                    'admin_profile',
                    urlconf='gbe.urls',
                    args=[troupe.contact.resourceitem_id]), request.path),
                 'text': "Update"}]
            bid_row['actions'] += [
                {'url': reverse('delete_profile',
                                urlconf='gbe.urls',
                                args=[troupe.contact.resourceitem_id]),
                 'text': "Delete"}]

        rows.append(bid_row)

    return render(request, 'gbe/profile_review.tmpl',
                  {'title': "Manage Troupes", 'header': header, 'rows': rows})
