import pytz
from django.db.models import(
    BooleanField,
    CharField,
    ForeignKey,
    OneToOneField,
    TextField,
    URLField,
)
from django.core.exceptions import (
    NON_FIELD_ERRORS,
    ValidationError,
)
from gbe.models import (
    Biddable,
    Conference,
    Performer,
    TechInfo,
    visible_bid_query,
)
from gbetext import (
    acceptance_states,
    act_alerts,
    act_not_unique,
    video_options,
)
from scheduler.models import ActItem
from settings import DATETIME_FORMAT
from django.utils.formats import date_format


class Act (Biddable, ActItem):
    '''
    A performance, either scheduled or proposed.
    Until approved, an Act is simply a proposal.
    '''
    performer = ForeignKey(Performer,
                           related_name='acts',
                           blank=True,
                           null=True)
    tech = OneToOneField(TechInfo, blank=True)
    video_link = URLField(blank=True)
    video_choice = CharField(max_length=2,
                             choices=video_options,
                             blank=True)
    shows_preferences = TextField(blank=True)
    other_performance = TextField(blank=True)
    why_you = TextField(blank=True)

    def clone(self):
        act = Act(
            performer=self.performer,
            tech=self.tech.clone(),
            video_link=self.video_link,
            video_choice=self.video_link,
            other_performance=self.other_performance,
            why_you=self.why_you,
            b_title=self.b_title,
            b_description=self.b_description,
            submitted=False,
            accepted=False,
            b_conference=Conference.objects.filter(
                status="upcoming").first()
        )
        act.save()
        return act

    def get_performer_profiles(self):
        '''
        Gets all of the performers involved in the act.
        '''
        return self.performer.get_profiles()

    def typeof(self):
        return self.__class__

    @property
    def audio(self):
        audio = None
        if self.tech and self.tech.audio:
            audio = self.tech.audio
        return audio

    @property
    def contact_email(self):
        return self.performer.contact_email

    @property
    def bio(self):
        return self.performer

    @property
    def schedule_ready(self):
        return self.accepted == 3

    @property
    def schedule_headers(self):
        # This list can change
        return ['Performer',
                'Act Title',
                'Photo Link',
                'Video Link',
                'Bio Link',
                'Order']

    @property
    def visible(self, current=True):
        return self.accepted == 3

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    @property
    def bid_review_header(self):
        return (['Performer',
                 'Act Title',
                 'Last Update',
                 'State',
                 'Show', ])

    @property
    def bid_review_summary(self):
        castings = ""
        for (show, role) in self.get_castings():
            if len(castings) > 0:
                castings += ", %s" % (str(show.eventitem))
            else:
                castings += str(show.eventitem)
            if len(role) > 0:
                castings += ' - %s' % role

        return [self.performer.name,
                self.b_title,
                date_format(self.updated_at, "DATETIME_FORMAT"),
                acceptance_states[self.accepted][1],
                castings]

    @property
    def complete(self):
        return (self.performer.complete and
                len(self.b_title) > 0 and
                len(self.b_description) > 0)

    def validate_unique(self, *args, **kwargs):
        # conference, title and performer contact should all be unique before
        # the act is saved.
        super(Act, self).validate_unique(*args, **kwargs)
        if Act.objects.filter(
                b_conference=self.b_conference,
                b_title=self.b_title,
                performer__contact=self.performer.contact
                ).exclude(pk=self.pk).exists():
            raise ValidationError({
                NON_FIELD_ERRORS: [act_not_unique, ]
            })

    @property
    def alerts(self):
        '''
        Return a list of alerts pertaining to this object
        '''
        this_act_alerts = []
        if self.complete:
            if self.submitted:
                this_act_alerts.append(
                    act_alerts['act_complete_submitted'] % self.id)
            else:
                this_act_alerts.append(
                    act_alerts['act_complete_not_submitted'] % self.id)
        else:
            if self.submitted:
                this_act_alerts.append(
                    act_alerts['act_incomplete_submitted'] % self.id)
            else:
                this_act_alerts.append(
                    act_alerts['act_incomplete_not_submitted'] % self.id)
        return this_act_alerts

    @property
    def bidder_is_active(self):
        return self.performer.contact.user_object.is_active

    @property
    def profile(self):
        return self.performer.contact

    def __str__(self):
        return "%s: %s" % (str(self.performer), self.b_title)

    class Meta:
        app_label = "gbe"
