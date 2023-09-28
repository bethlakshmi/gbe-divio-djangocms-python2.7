from django.views.generic import View
from django.views.decorators.cache import never_cache
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

    @never_cache
    def post(self, request, *args, **kwargs):
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
            roles=["Volunteer", "Pending Volunteer"],
            get_peers=True)
        bookings = []
        for person in volunteers.people:
            if person.public_id == self.owner.pk and (
                    person.public_class == self.owner.__class__.__name__):
                bookings += [person]
        schedule_response = None
        changed_occurrences = []
        approval_needed_events = []
        if kwargs['state'] == 'on' and len(bookings) == 0:
            paired_event, schedule_response = self.book_volunteer(
                request,
                occ_response.occurrence)
            changed_occurrences += [occ_response.occurrence]
            if occ_response.occurrence.approval_needed:
                approval_needed_events += [occ_response.occurrence]

            if paired_event:
                paired_event_OK, schedule_response = self.book_volunteer(
                    request,
                    occ_response.occurrence.peer)
                if occ_response.occurrence.peer.approval_needed:
                    approval_needed_events += [occ_response.occurrence.peer]
                changed_occurrences += [occ_response.occurrence.peer]
                if paired_event_OK:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="SET_PAIR",
                        defaults={
                            'summary': "User Volunteers for Paired Event",
                            'description': paired_event_set_vol_msg})
                    msg = (user_message[0].description +
                        occ_response.occurrence.title + ', ' +
                        occ_response.occurrence.peer.title)
                    messages.success(request, msg)
        elif kwargs['state'] == 'off' and len(bookings) > 0:
            # if this person has volunteered, and is withdrawing
            success = True
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
                if schedule_response.booking_id:
                    changed_occurrences += [booking.occurrence]
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="REMOVE_%s" % role.replace(" ", "_").upper(),
                        defaults={
                            'summary': default_summary,
                            'description': default_message})
                    messages.success(request, user_message[0].description)
        if schedule_response and schedule_response.booking_id:
            if kwargs['state'] == 'on' and len(approval_needed_events) >= 0:
                email_status = send_awaiting_approval_mail(
                    "volunteer",
                    self.owner.contact_email,
                    self.owner.get_badge_name(),
                    approval_needed_events)
            elif kwargs['state'] == 'off' and (
                    occ_response.occurrence.approval_needed):
                email_status = send_bid_state_change_mail(
                    "volunteer",
                    self.owner.contact_email,
                    self.owner.get_badge_name(),
                    occ_response.occurrence.title,
                    4)
            else:
                email_status = send_schedule_update_mail("Volunteer",
                                                         self.owner)
            staff_status = send_volunteer_update_to_staff(
                self.owner,
                self.owner,
                changed_occurrences,
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

        # if this person hasn't volunteered yet, and wants to
        person = Person(
            users=[self.owner.user_object],
            role="Volunteer",
            public_id=self.owner.pk,
            public_class=self.owner.__class__.__name__)
        default_summary = "User has volunteered"
        default_message = set_volunteer_msg
        if occurrence.approval_needed:
            person.role = "Pending Volunteer"
            default_summary = "User is pending"
            default_message = set_pending_msg

        schedule_response = set_person(occurrence.pk, person)
        show_general_status(request,
                            schedule_response,
                            self.__class__.__name__,
                            False)
        if len(schedule_response.errors) == 0 and (
                schedule_response.booking_id):
            if occurrence.peer is None:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_%s" % person.role.replace(" ", "_").upper(),
                    defaults={
                        'summary': default_summary,
                        'description': default_message})
                messages.success(request, user_message[0].description)
            else:
                paired_event = True

        return paired_event, schedule_response
