from django.db.models import (
    CASCADE,
    TextField,
    ForeignKey,
    IntegerField,
    BooleanField,
)
from gbetext import (
    acceptance_states,
    boolean_options,
    volunteer_shift_options,
)
from gbe.models import (
    Biddable,
    Profile,
    visible_bid_query,
)
from django.utils.formats import date_format
from scheduler.idd import get_schedule
import pytz


class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    profile = ForeignKey(Profile,
                         on_delete=CASCADE,
                         related_name="volunteering")
    number_shifts = IntegerField(choices=volunteer_shift_options)
    availability = TextField(blank=True)
    unavailability = TextField(blank=True)
    opt_outs = TextField(blank=True)
    pre_event = BooleanField(choices=boolean_options, default=False)
    background = TextField()

    def __str__(self):
        return self.profile.display_name

    @property
    def bidder_is_active(self):
        return self.profile.user_object.is_active

    @property
    def interest_list(self):
        return [
            interest.interest.interest
            for interest in self.volunteerinterest_set.filter(rank__gt=3)]

    @property
    def bid_review_header(self):
        return (['Name',
                 'Email',
                 'Hotel',
                 '# of Hours',
                 'Scheduling Info',
                 'Interests',
                 'Pre-event',
                 'Background',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        interest_string = ''
        for interest in self.interest_list:
            interest_string += interest + ', \n'
        commitments = ''

        response = get_schedule(user=self.profile.user_object,
                                labels=[self.b_conference.conference_slug])
        for item in response.schedule_items:
            start_time = date_format(item.event.start_time, 'DATETIME_FORMAT')
            end_time = date_format(item.event.end_time, 'TIME_FORMAT')

            commitment_string = "%s - %s to %s, \n " % (
                str(item.event),
                start_time,
                end_time)
            commitments += commitment_string
        format_string = "Commitments: %s"
        scheduling = format_string % commitments
        return [self.profile.display_name,
                self.profile.user_object.email,
                self.profile.preferences.in_hotel,
                self.number_shifts,
                scheduling,
                interest_string,
                self.pre_event,
                self.background,
                acceptance_states[self.accepted][1]]

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"
