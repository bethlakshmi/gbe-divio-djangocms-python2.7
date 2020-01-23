from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from settings import GBE_DATETIME_FORMAT
from gbe.models import (
    Conference,
    Profile,
    StaffArea,
    UserMessage,
)
from gbe.functions import validate_perms
from scheduler.idd import (
    get_assignments,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from gbetext import (
    volunteer_action_map,
    set_volunteer_role_summary,
    set_volunteer_role_msg,
    volunteer_allocate_email_fail_msg,
)
from gbe.email.functions import (
    send_bid_state_change_mail,
    send_schedule_update_mail,
    send_volunteer_update_to_staff,
)
from scheduler.data_transfer import Person


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
        action = ""

        for pending_offer in pending.assignments:
            action_links = {
                'email': reverse('mail_to_individual',
                                 urlconf='gbe.email.urls',
                                 args=[pending_offer.person.public_id])}
            for action in ['approve', 'reject', 'waitlist']:
                if action in volunteer_action_map and (
                        volunteer_action_map[action]['role'] == (
                            pending_offer.person.role)):
                    action_links[action] = None
                else:
                    action_links[action] = reverse(
                        self.review_list_view_name,
                        urlconf='gbe.scheduling.urls',
                        args=[action, 
                              pending_offer.person.public_id,
                              pending_offer.booking_id])
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
                'label': pending_offer.person.label,
                'action_links': action_links}
            if hasattr(pending_offer.occurrence, 'container_event'):
                container = pending_offer.occurrence.container_event
                row['parent_event'] = container.parent_event
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

    def send_notifications(self, request, response, state, person):
        if state == 3:
            email_status = send_schedule_update_mail(
                "Volunteer",
                person.user.profile)
        else:
            email_status = send_bid_state_change_mail(
                "volunteer",
                person.user.profile.contact_email,
                person.user.profile.get_badge_name(),
                response.occurrence,
                state)
        staff_status = send_volunteer_update_to_staff(
            self.reviewer,
            person.user.profile,
            response.occurrence,
            person.role,
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
        state = volunteer_action_map[kwargs['action']]['state']
        if kwargs['action'] == "approve":
            check = True
        profile = get_object_or_404(Profile, pk=kwargs['public_id'])
        person = Person(
            user=profile.user_object,
            public_id=profile.pk,
            role=volunteer_action_map[kwargs['action']]['role'],
            booking_id=kwargs['booking_id'],
            worker=None)
        response = set_person(person=person)
        show_general_status(request, response, self.__class__.__name__)
        if not response.errors:
            self.changed_id = response.booking_id
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="SET_%s" % person.role,
                defaults={
                    'summary': set_volunteer_role_summary % person.role,
                    'description': set_volunteer_role_msg % person.role})
            full_msg = '%s Person: %s<br/>Event: %s, Start Time: %s' % (
                user_message[0].description,
                str(profile),
                str(response.occurrence),
                response.occurrence.starttime.strftime(
                    GBE_DATETIME_FORMAT))
            messages.success(request, full_msg)
            self.send_notifications(request, response, state, person)

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request)
        if 'action' in kwargs and 'booking_id' in kwargs and (
                'public_id' in kwargs):
            self.set_status(request, kwargs)

        return render(request,
                      self.template,
                      self.make_context(self.get_list(request)))
