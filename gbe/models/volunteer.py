from django.db.models import (
    TextField,
    ForeignKey,
    IntegerField,
    BooleanField,
    ManyToManyField,
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
    VolunteerWindow,
)
from django.utils.formats import date_format
import pytz


class Volunteer(Biddable):
    '''
    Represents a conference attendee's participation as a volunteer.
    '''
    profile = ForeignKey(Profile, related_name="volunteering")
    number_shifts = IntegerField(choices=volunteer_shift_options)
    availability = TextField(blank=True)
    unavailability = TextField(blank=True)
    opt_outs = TextField(blank=True)
    pre_event = BooleanField(choices=boolean_options, default=False)
    background = TextField()
    available_windows = ManyToManyField(
        VolunteerWindow,
        related_name="availablewindow_set",
        blank=True)
    unavailable_windows = ManyToManyField(
        VolunteerWindow,
        related_name="unavailablewindow_set",
        blank=True)

    def __unicode__(self):
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
        availability_string = ''
        unavailability_string = ''
        for window in self.available_windows.all():
            availability_string += unicode(window) + ', \n'
        for window in self.unavailable_windows.all():
            unavailability_string += unicode(window) + ', \n'

        commitments = ''

        for event in self.profile.get_schedule(self.b_conference):
            start_time = date_format(event.start_time, 'DATETIME_FORMAT')
            end_time = date_format(event.end_time, 'TIME_FORMAT')

            commitment_string = "%s - %s to %s, \n " % (
                str(event),
                start_time,
                end_time)
            commitments += commitment_string
        format_string = "Availability: %s\n Conflicts: %s\n Commitments: %s"
        scheduling = format_string % (availability_string,
                                      unavailability_string,
                                      commitments)
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

    def check_available(self, start, end):
        available = "Not Available"
        start = start.replace(tzinfo=pytz.utc)
        end = end.replace(tzinfo=pytz.utc)
        for window in self.available_windows.all():
            starttime = window.start_timestamp().replace(tzinfo=pytz.utc)
            endtime = window.end_timestamp().replace(tzinfo=pytz.utc)

            if start == starttime:
                available = "Available"
            elif (start > starttime and
                  start < endtime):
                available = "Available"
            elif (start < starttime and
                  end > starttime):
                available = "Available"
        return available

    class Meta:
        app_label = "gbe"
