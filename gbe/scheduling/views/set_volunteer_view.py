from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.data_transfer import Person
from scheduler.idd import (
    get_occurrence,
    get_bookings,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import UserMessage
from gbe.functions import check_user_and_redirect
from gbetext import (
    set_volunteer_msg,
    unset_volunteer_msg,
    set_pending_msg,
    unset_pending_msg,
)
from gbe.email.functions import send_schedule_update_mail


class SetVolunteerView(View):

    @never_cache
    def get(self, request, *args, **kwargs):
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
        occurrence_id = int(kwargs['occurrence_id'])
        occ_response = get_occurrence(occurrence_id)
        show_general_status(request, occ_response, self.__class__.__name__)
        if occ_response.errors:
            return HttpResponseRedirect(request.GET['next'])

        volunteers = get_bookings(
            [occurrence_id],
            roles=["Volunteer", "Pending Volunteer"])
        bookings = []
        for person in volunteers.people:
            if person.user == self.owner.user_object:
                bookings += [person]

        if kwargs['state'] == 'on' and len(bookings) == 0:
            # if this person hasn't volunteered yet, and wants to
            role = "Volunteer"
            default_summary = "User has volunteered"
            default_message = set_volunteer_msg
            if occ_response.occurrence.approval_needed:
                role = "Pending Volunteer"
                default_summary = "User is pending"
                default_message = set_pending_msg
            person = Person(
                user=self.owner.user_object,
                role=role)
            response = set_person(occurrence_id, person)
            show_general_status(request,
                                response,
                                self.__class__.__name__)
            if len(response.errors) == 0 and response.booking_id:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_%s" % role.replace(" ","_").upper(),
                    defaults={
                        'summary': default_summary,
                        'description': default_message})
                messages.success(request, user_message[0].description)
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
                response = remove_booking(occurrence_id,
                                          booking.booking_id)
                show_general_status(request,
                                    response,
                                    self.__class__.__name__)
                if response.booking_id:
                    user_message = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="REMOVE_%s" % role.replace(" ","_").upper(),
                        defaults={
                            'summary': default_summary,
                            'description': default_message})
                    messages.success(request, user_message[0].description)
        if request.GET.get('next', None):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('home', urlconf='gbe.urls')
        return HttpResponseRedirect(redirect_to)

    def dispatch(self, *args, **kwargs):
        return super(SetVolunteerView, self).dispatch(*args, **kwargs)
