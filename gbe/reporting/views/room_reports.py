from gbe_utils.mixins import (
    ConferenceListView,
    RoleRequiredMixin,
)
from gbe.models import (
    Bio,
    Class,
    Profile,
    Room,
)
from scheduler.idd import get_people
from gbetext import (
    class_styles,
    class_roles,
    privileged_event_roles,
)


class RoomScheduleView(RoleRequiredMixin, ConferenceListView):
    model = Room
    template_name = 'gbe/report/room_schedule.tmpl'
    view_permissions = 'any'
    room_set_key = 'events'

    def get_queryset(self):
        return self.model.objects.filter(
            conferences=self.conference).order_by('name')

    def get_conf_days(self):
        conf_days = self.conference.conferenceday_set.all()
        tmp_days = []
        for position in range(0, len(conf_days)):
            tmp_days.append(conf_days[position].day)
        return tmp_days

    def make_day_events(self, booking):
        response = get_people(event_ids=[booking.pk],
                              roles=class_roles+privileged_event_roles)
        people_set = []
        for people in response.people:
            people_set += [{
                "role": people.role,
                "person": eval(people.public_class).objects.get(
                    pk=people.public_id)}]
        return [{'booking': booking, 'people': people_set}]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        conf_days = self.get_conf_days() 

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
                    if current_day in conf_days and len(day_events) > 0:
                        room_set += [{'room': room,
                                      'date': current_day,
                                      self.room_set_key: day_events}]
                    current_day = booking.start_time.date()
                    day_events = []

                event_set = self.make_day_events(booking)
                if event_set is not None:
                    day_events += event_set

            if current_day in conf_days and len(day_events) > 0:
                room_set += [{'room': room,
                              'date': current_day,
                              self.room_set_key: day_events}]
        context['room_date'] = room_set
        return context

class RoomSetupView(RoomScheduleView):
    template_name = 'gbe/report/room_setup.tmpl'
    room_set_key = 'bookings'

    def make_day_events(self, booking):
        if booking.event_style in class_styles:
            return [{'event': booking,
                     'class': Class.objects.get(pk=booking.connected_id)}]
        return None
