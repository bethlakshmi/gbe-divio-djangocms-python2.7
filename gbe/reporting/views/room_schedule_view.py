from gbe_utils.mixins import (
    ConferenceListView,
    RoleRequiredMixin,
)
from gbe.models import (
    Bio,
    Profile,
    Room,
)
from scheduler.idd import get_people
from gbetext import (
    class_roles,
    privileged_event_roles,
)


class RoomScheduleView(RoleRequiredMixin, ConferenceListView):
    model = Room
    template_name = 'gbe/report/room_schedule.tmpl'
    view_permissions = 'any'

    def get_queryset(self):
        return self.model.objects.filter(
            conferences=self.conference).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        conf_days = self.conference.conferenceday_set.all()
        tmp_days = []
        for position in range(0, len(conf_days)):
            tmp_days.append(conf_days[position].day)
        conf_days = tmp_days

        # rearrange the data into the format of:
        #  - room & date of booking
        #       - list of bookings
        # this lets us have 1 table per day per room
        room_set = []
        for room in self.get_queryset():
            day_events = []
            current_day = None
            for booking in room.get_bookings:
                if not current_day:
                    current_day = booking.start_time.date()
                if current_day != booking.start_time.date():

                    if current_day in conf_days:
                        room_set += [{'room': room,
                                      'date': current_day,
                                      'events': day_events}]
                    current_day = booking.start_time.date()
                    day_events = []
                response = get_people(event_ids=[booking.pk],
                                      roles=class_roles+privileged_event_roles)
                people_set = []
                for people in response.people:
                    people_set += [{
                        "role": people.role,
                        "person": eval(people.public_class).objects.get(
                            pk=people.public_id)}]
                day_events += [{'booking': booking,
                                'people': people_set}]
            if current_day in conf_days:
                room_set += [{'room': room,
                              'date': current_day,
                              'events': day_events}]
        context['room_date'] = room_set
        return context
