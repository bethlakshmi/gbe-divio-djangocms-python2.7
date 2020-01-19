from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import Http404
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.formats import date_format
from datetime import timedelta
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
    URL_DATE,
)
from gbe.models import (
    Conference,
    Event,
    GenericEvent,
    StaffArea,
    Profile,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    conference_list,
    validate_perms,
)
from scheduler.idd import get_assignments
from gbe.scheduling.views.functions import show_general_status


class ApproveVolunteerView(View):
    template = 'gbe/scheduling/approve_volunteer.tmpl'
    conference = None
    reviewer_permissions = ('Volunteer Coordinator', 'Staff Lead')
    review_list_view_name = 'approve_volunteer'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApproveVolunteerView, self).dispatch(*args, **kwargs)

    def get_list(self, request):
        pending = get_assignments(roles=["Pending Volunteer"], 
                                  labels=[self.conference.conference_slug])
        show_general_status(
            request, pending, self.__class__.__name__)
        rows = []
        for pending_offer in pending.assignments:
            row = {
                'volunteer': Profile.objects.get(
                    pk=pending_offer.person.public_id),
                'occurrence': pending_offer.occurrence,
                'staff_areas': StaffArea.objects.filter(
                    conference=self.conference,
                    slug__in=pending_offer.occurrence.labels.values_list(
                        'text', 
                        flat=True)),
                'status': "",
                'action_links': {
                    'approve': reverse(self.review_list_view_name,
                                       urlconf='gbe.scheduling.urls',
                                       args=["approve", 
                                             pending_offer.booking_id]),
                    'waitlist': reverse(self.review_list_view_name,
                                        urlconf='gbe.scheduling.urls',
                                        args=["waitlist", 
                                              pending_offer.booking_id]),
                    'reject': reverse(self.review_list_view_name,
                                      urlconf='gbe.scheduling.urls',
                                      args=["reject", 
                                            pending_offer.booking_id]),
                    'email': reverse('mail_to_individual',
                                     urlconf='gbe.email.urls',
                                     args=[pending_offer.person.public_id]),}
                }
            if hasattr(pending_offer.occurrence, 'container_event'):
                row['parent_event'] = pending_offer.occurrence.container_event.parent_event
            if not row['volunteer'].is_active:
                row['status'] = "danger"
            elif pending_offer.occurrence.volunteer_count >= (
                    pending_offer.occurrence.max_volunteer):
                row['status'] = "warning"
            rows.append(row)
        return rows

    def make_context(self, rows):
        return {
            'rows': rows,
            'conference_slugs': self.conference_slugs,
            'conference': self.conference}

    @never_cache
    def get(self, request, *args, **kwargs):
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        if request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            self.conference = Conference.current_conf()

        self.conference_slugs = Conference.all_slugs()
        return render(request,
                      self.template,
                      self.make_context(self.get_list(request)))
