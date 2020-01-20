from django.views.generic import View
from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings import GBE_DATETIME_FORMAT
from gbe.models import (
    Conference,
    StaffArea,
    UserMessage,
)
from gbe.functions import validate_perms
from scheduler.idd import (
    get_assignments,
    update_assignment,
)
from gbe.scheduling.views.functions import show_general_status
from gbetext import (
    set_volunteer_role_summary,
    set_volunteer_role_msg,
)
from gbe.email.functions import (
    send_schedule_update_mail,
    send_volunteer_update_to_staff,
)


class ApproveVolunteerView(View):
    template = 'gbe/scheduling/approve_volunteer.tmpl'
    conference = None
    reviewer_permissions = ('Volunteer Coordinator', 'Staff Lead')
    review_list_view_name = 'approve_volunteer'
    changed_id = -1

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ApproveVolunteerView, self).dispatch(*args, **kwargs)

    def get_list(self, request):
        pending = get_assignments(
            roles=["Pending Volunteer", "Waitlisted", "Rejected"], 
            labels=[self.conference.conference_slug])
        show_general_status(request, pending, self.__class__.__name__)
        rows = []
        for pending_offer in pending.assignments:
            row = {
                'volunteer': pending_offer.person.user.profile,
                'occurrence': pending_offer.occurrence,
                'staff_areas': StaffArea.objects.filter(
                    conference=self.conference,
                    slug__in=pending_offer.occurrence.labels.values_list(
                        'text', 
                        flat=True)),
                'state': pending_offer.person.role.split(' ', 1)[0],
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
            if pending_offer.booking_id == self.changed_id:
                row['status'] = 'success'
            elif not row['volunteer'].is_active:
                row['status'] = "danger"
            elif pending_offer.occurrence.volunteer_count >= (
                    pending_offer.occurrence.max_volunteer):
                row['status'] = "warning"
            elif pending_offer.person.role == "Pending Volunteer":
                row['status'] = "info"
            rows.append(row)
        return rows

    def make_context(self, rows):
        return {
            'rows': rows,
            'conference_slugs': self.conference_slugs,
            'conference': self.conference}

    def groundwork(self, request):
        self.reviewer = validate_perms(request, self.reviewer_permissions)
        if request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        else:
            self.conference = Conference.current_conf()
        self.conference_slugs = Conference.all_slugs()

    def send_notifications(self, request, response):
        email_status = send_schedule_update_mail(
            "Volunteer",
            response.assignments[0].person.user.profile)
        staff_status = send_volunteer_update_to_staff(
            response.assignments[0].person.user.profile,
            response.assignments[0].occurrence,
            response.assignments[0].person.role,
            response)
        if email_status or staff_status:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="EMAIL_FAILURE",
                defaults={
                    'summary': "Email Failed",
                    'description': volunteer_allocate_email_fail_msg})
            messages.error(
                request,
                user_message[0].description + "status code: ")

    def set_status(self, request, kwargs):
        check = False
        role = "Pending Volunteer"
        if kwargs['action'] == "approve":
            role = "Volunteer"
            check = True
        elif kwargs['action'] == "waitlist":
            role = "Waitlisted"
        elif kwargs['action'] == "reject":
            role = "Rejected"
        response = update_assignment(kwargs['booking_id'], role, check)
        show_general_status(request, response, self.__class__.__name__)
        if response.assignments:
            self.changed_id = response.assignments[0].booking_id
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SET_%s" % role,
                defaults={
                    'summary': set_volunteer_role_summary % role,
                    'description': set_volunteer_role_msg % role})
            full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                user_message[0].description,
                str(response.assignments[0].person.user.profile),
                str(response.assignments[0].occurrence),
                response.assignments[0].occurrence.starttime.strftime(
                    GBE_DATETIME_FORMAT))
            messages.success(request, full_msg)
            self.send_notifications(request, response)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request)
        if 'action' in kwargs and 'booking_id' in kwargs:
            self.set_status(request, kwargs)

        return render(request,
                      self.template,
                      self.make_context(self.get_list(request)))
