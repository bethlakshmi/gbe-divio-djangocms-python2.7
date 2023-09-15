from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from gbe_logging import log_func
from gbe.models import (
    Bio,
    UserMessage,
)
from gbe.functions import validate_perms
from gbetext import troupe_intro_msg
from scheduler.idd import get_bookable_people


class ReviewTroupesView(View):
    reviewer_permissions = ('Act Coordinator', 'Registrar',)
    header = ['Troupe', 'Contact', 'Members', 'Action']
    title = "Manage Troupes"

    @never_cache
    @log_func
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        admin_profile = validate_perms(request, self.reviewer_permissions)
        troupes = Bio.objects.filter(contact__user_object__is_active=True,
                                     multiple_performers=True)
        rows = []
        intro = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="INTRODUCTION",
            defaults={
                'summary': "Top of Page Instructions",
                'description': troupe_intro_msg})
        for troupe in troupes:
            bid_row = {}
            members = ""

            if not troupe.acts.filter(accepted=3).exclude(
                    b_conference__status='completed').exists():
                members = "<i>No accepted acts in this conference</i>"
            else:
                for act in troupe.acts.filter(accepted=3).exclude(
                        b_conference__status='completed'):
                    response = get_bookable_people(
                        troupe.pk,
                        troupe.__class__.__name__,
                        commitment_class_name=act.__class__.__name__,
                        commitment_class_id=act.pk)
                    for member in response.people[0].users:
                        if member.is_active:
                            members += "%s,<br>" % member.profile.display_name

            bid_row['profile'] = (
                troupe.name,
                "%s<br>(<a href='%s'>%s</a>)" % (
                    troupe.contact.display_name,
                    reverse(
                        'mail_to_individual',
                        urlconf='gbe.email.urls',
                        args=[troupe.contact.pk]),
                    troupe.contact.user_object.email),
                members)
            bid_row['id'] = troupe.pk
            bid_row['actions'] = [
                {'url': reverse(
                    'bio_view',
                    urlconf='gbe.urls',
                    args=[troupe.pk]),
                 'text': "View Troupe"},
                {'url': reverse(
                    'admin_landing_page',
                    urlconf='gbe.urls',
                    args=[troupe.contact.pk]),
                 'text': "View Contact Landing Page"},
                {'url': reverse(
                    'mail_to_individual',
                    urlconf='gbe.email.urls',
                    args=[troupe.contact.pk]),
                 'text': "Email Contact"}
            ]
            rows.append(bid_row)

        return render(request, 'gbe/profile_review.tmpl', {
            'page_title': "Manage Troupes",
            'view_title': "Manage Troupes",
            'intro_text': intro[0].description,
            'columns': self.header,
            'rows': rows,
            'order': 0,
            'title': self.title})
