from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.data_transfer import Person
from scheduler.idd import (
    get_bookings,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import UserMessage
from gbe.functions import check_user_and_redirect
from gbetext import (
    set_favorite_msg,
    unset_favorite_msg,
)


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
        interested = get_bookings([occurrence_id],
                                  roles=["Interested"])
        bookings = []
        for person in interested.people:
            if person.user == self.owner.user_object:
                bookings += [person.booking_id]

        if kwargs['state'] == 'on' and len(bookings) == 0:
            person = Person(
                user=self.owner.user_object,
                role="Interested")
            response = set_person(occurrence_id, person)
            show_general_status(request,
                                response,
                                self.__class__.__name__)
            if len(response.errors) == 0 and response.booking_id:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="SET_FAVORITE",
                    defaults={
                        'summary': "User has shown interest",
                        'description': set_favorite_msg})
                messages.success(request, user_message[0].description)
        elif kwargs['state'] == 'off' and len(bookings) > 0:
            success = True
            for booking_id in bookings:
                response = remove_booking(occurrence_id,
                                          booking_id)
                show_general_status(request,
                                    response,
                                    self.__class__.__name__)
            if response.booking_id:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="REMOVE_FAVORITE",
                    defaults={
                        'summary': "User has shown lack of interest",
                        'description': unset_favorite_msg})
                messages.success(request, user_message[0].description)
        if request.GET.get('next', None):
            redirect_to = request.GET['next']
        else:
            redirect_to = reverse('home', urlconf='gbe.urls')
        return HttpResponseRedirect(redirect_to)

    def dispatch(self, *args, **kwargs):
        return super(SetFavoriteView, self).dispatch(*args, **kwargs)
