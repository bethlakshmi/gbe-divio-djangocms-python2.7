from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from scheduler.data_transfer import Person
from scheduler.idd import (
    get_occurrence,
    get_bookings,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import UserMessage
from gbe.forms import InvolvedProfileForm
from gbe.functions import (
    check_user_and_redirect,
    validate_perms,
)
from gbetext import (
    paired_event_set_vol_msg,
    set_volunteer_msg,
    unset_volunteer_msg,
    set_pending_msg,
    unset_pending_msg,
    vol_opp_full_msg,
    vol_prof_update_failure,
    volunteer_allocate_email_fail_msg,
)
from gbe.email.functions import (
    send_awaiting_approval_mail,
    send_bid_state_change_mail,
    send_schedule_update_mail,
    send_volunteer_update_to_staff,
)


class SetVolunteerView(View):

    @method_decorator(never_cache, name="get")
    def post(self, request, *args, **kwargs):
        warnings = []
        errors = []
        redirect_to = request.GET.get(
            "next", reverse('volunteer_signup',
                            urlconf='gbe.scheduling.urls'))
        this_url = reverse(
            'set_volunteer',
            args=[kwargs['occurrence_id'], kwargs['state']],
            urlconf='gbe.scheduling.urls')
        response = check_user_and_redirect(
            request,
            this_url,
            self.__class__.__name__)
        if response['error_url']:
            return HttpResponseRedirect(response['error_url'])
        self.owner = response['owner']
        if 'first_name' in request.POST.keys():
            form = InvolvedProfileForm(
                request.POST,
                instance=self.owner,
                initial={'first_name': request.user.first_name,
                         'last_name': request.user.last_name})
            if form.is_valid():
                form.save()
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="PROFILE_UPDATE_FAILED",
                    defaults={
                        'summary': "Profile Update Failed",
                        'description': vol_prof_update_failure})
                messages.error(
                    request,
                    user_message[0].description + "status code: ")
                return HttpResponseRedirect(reverse(
                    'volunteer_signup',
                    urlconf='gbe.scheduling.urls'))
        occurrence_id = int(kwargs['occurrence_id'])
        occ_response = get_occurrence(occurrence_id)
        show_general_status(request, occ_response, self.__class__.__name__)
        if occ_response.errors:
            return HttpResponseRedirect(redirect_to)

        volunteers = get_bookings(
            [occurrence_id],
            roles=["Volunteer", "Pending Volunteer"])
        bookings = []
        for person in volunteers.people:
            if person.public_id == self.owner.pk and (
                    person.public_class == self.owner.__class__.__name__):
                bookings += [person]
        schedule_response = None
        approval_needed_events = []
        if kwargs['state'] == 'on' and len(bookings) == 0:
            if occ_response.occurrence.extra_volunteers() >= 0 or (
                    occ_response.occurrence.peer is not None and
                    occ_response.occurrence.peer.extra_volunteers() >= 0):
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="VOL_OPP_FULL",
                    defaults={
                        'summary': "Volunteer slot or Linked slot is full",
                        'description': vol_opp_full_msg})
                messages.success(request, user_message[0].description)
            else:
                schedule_response = self.book_volunteer(
                    request,
                    occ_response.occurrence)
                if occ_response.occurrence.approval_needed:
                    approval_needed_events += [occ_response.occurrence]
                if occ_response.occurrence.peer is not None and (
                        occ_response.occurrence.peer.approval_needed):
                    approval_needed_events = [occ_response.occurrence,
                                              occ_response.occurrence.peer]

        elif kwargs['state'] == 'off' and len(bookings) > 0:
            # if this person has volunteered, and is withdrawing
            success = True
            approval_needed = False
            for booking in bookings:
                role = booking.role
                default_summary = "User withdrew"
                default_message = unset_volunteer_msg
                if role == "Pending Volunteer":
                    default_summary = "Pending user withdrew"
                    default_message = unset_pending_msg
                schedule_response = remove_booking(booking.occurrence.pk,
                                                   booking.booking_id)
                show_general_status(request,
                                    schedule_response,
                                    self.__class__.__name__)
                for item in schedule_response.occurrences:
                    if item.approval_needed:
                        approval_needed_events += [item]
                if len(schedule_response.occurrences) > 0:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="REMOVE_%s" % role.replace(" ", "_").upper(),
                        defaults={
                            'summary': default_summary,
                            'description': default_message})
                    messages.success(request, user_message[0].description)

        if schedule_response and len(schedule_response.booking_ids) > 0:
            if kwargs['state'] == 'on' and len(approval_needed_events) > 0:
                email_status = send_awaiting_approval_mail(
                    "volunteer",
                    self.owner.contact_email,
                    self.owner.get_badge_name(),
                    approval_needed_events)

            elif kwargs['state'] == 'off' and len(approval_needed_events) > 0:
                titles = ""
                for event in approval_needed_events:
                    if len(titles) > 0:
                        titles = titles + ", and " + event.title
                    else:
                        titles = event.title
                email_status = send_bid_state_change_mail(
                    "volunteer",
                    self.owner.contact_email,
                    self.owner.get_badge_name(),
                    titles,
                    4)
            else:
                email_status = send_schedule_update_mail("Volunteer",
                                                         self.owner)
            staff_status = send_volunteer_update_to_staff(
                self.owner,
                self.owner,
                schedule_response.occurrences,
                kwargs['state'],
                schedule_response)
            if (email_status or staff_status) and validate_perms(
                    request,
                    'any',
                    require=False):
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="EMAIL_FAILURE",
                    defaults={
                        'summary': "Email Failed",
                        'description': volunteer_allocate_email_fail_msg})
                messages.error(
                    request,
                    user_message[0].description + "status code: ")
        return HttpResponseRedirect(redirect_to)

    def book_volunteer(self, request, occurrence):
        paired_event = False
        approval_needed = False

        # if this person hasn't volunteered yet, and wants to
        person = Person(
            users=[self.owner.user_object],
            role="Volunteer",
            public_id=self.owner.pk,
            public_class=self.owner.__class__.__name__)
        if occurrence.approval_needed or (occurrence.peer is not None and
                                          occurrence.peer.approval_needed):
            person.role = "Pending Volunteer"
            approval_needed = True

        schedule_response = set_person(occurrence.pk, person)
        show_general_status(request,
                            schedule_response,
                            self.__class__.__name__,
                            False)
        if len(schedule_response.errors) == 0:
            msg = ""
            if approval_needed:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_PENDING_VOLUNTEER",
                    defaults={
                        'summary': "User is pending",
                        'description': set_pending_msg})
                msg = user_message[0].description
            elif len(schedule_response.booking_ids) == 1:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_VOLUNTEER",
                    defaults={
                        'summary': "User has volunteered",
                        'description': set_volunteer_msg})
                msg = user_message[0].description
            elif len(schedule_response.booking_ids) > 1:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_PAIR",
                    defaults={'summary': "User Volunteers for Paired Event",
                              'description': paired_event_set_vol_msg})
                msg = (user_message[0].description +
                       occurrence.title + ', ' +
                       occurrence.peer.title)
            messages.success(request, msg)

        return schedule_response
