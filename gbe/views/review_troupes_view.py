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
                                     multiple_performers=False)
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
            # TODO - build an API for getting this - cause this won't work
            for member in troupe.membership.filter(
                    contact__user_object__is_active=True):
                members += "%s,<br>" % member.name
            bid_row['profile'] = (
                troupe.name,
                "%s<br>(<a href='%s'>%s</a>)" % (
                    troupe.contact.display_name,
                    reverse(
                        'mail_to_individual',
                        urlconf='gbe.email.urls',
                        args=[troupe.contact.resourceitem_id]),
                    troupe.contact.user_object.email),
                members)
            bid_row['id'] = troupe.pk
            bid_row['actions'] = [
                {'url': reverse(
                    'troupe_view',
                    urlconf='gbe.urls',
                    args=[troupe.pk]),
                 'text': "View Troupe"},
                {'url': reverse(
                    'admin_landing_page',
                    urlconf='gbe.urls',
                    args=[troupe.contact.resourceitem_id]),
                 'text': "View Contact Landing Page"},
                {'url': reverse(
                    'mail_to_individual',
                    urlconf='gbe.email.urls',
                    args=[troupe.contact.resourceitem_id]),
                 'text': "Email Contact"}
            ]
            rows.append(bid_row)

        return render(request, 'gbe/profile_review.tmpl', {
            'title': "Manage Troupes",
            'intro': intro[0].description,
            'columns': self.header,
            'rows': rows,
            'order': 0,
            'title': self.title})
