import pytz
from settings import GBE_TABLE_FORMAT
from django.db.models import(
    CASCADE,
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
    Bio,
    Conference,
    Performer,
    TechInfo,
)
from gbetext import (
    acceptance_states,
    act_not_unique,
    video_options,
)
from scheduler.idd import get_schedule


class Act (Biddable):
    '''
    A performance, either scheduled or proposed.
    Until approved, an Act is simply a proposal.
    '''
    performer = ForeignKey(Performer,
                           on_delete=CASCADE,
                           related_name='acts',
                           blank=True,
                           null=True)
    bio = ForeignKey(Bio,
                     on_delete=CASCADE,
                     related_name='acts',
                     blank=True,
                     null=True)
    tech = OneToOneField(TechInfo, on_delete=CASCADE, blank=True)
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
        cast_shows = []
        for item in get_schedule(commitment=self,
                                 roles=["Performer", "Waitlisted"]
                                 ).schedule_items:
            if item.event.event_style == "Show" and (
                    item.event.pk not in cast_shows):
                if len(castings) > 0:
                    castings += ", %s" % str(item.event.title)
                else:
                    castings += str(item.event.title)
                if item.commitment.role and len(item.commitment.role) > 0:
                    castings += ' - %s' % item.commitment.role
                cast_shows += [item.event.pk]

        return [self.performer.name,
                self.b_title,
                self.updated_at.strftime(GBE_TABLE_FORMAT),
                acceptance_states[self.accepted][1],
                castings]

    @property
    def is_complete(self):
        if self.tech.is_complete:
            if self.tech.confirm_no_rehearsal:
                return True
            for item in get_schedule(commitment=self).schedule_items:
                if item.event.event_style == 'Rehearsal Slot':
                    return True
        return False

    def validate_unique(self, *args, **kwargs):
        # conference, title and performer contact should all be unique before
        # the act is saved.
        super(Act, self).validate_unique(*args, **kwargs)
        if self.performer is None or not self.performer.contact:
            raise ValidationError({'performer': "Performer is not valid"})
        if Act.objects.filter(
                b_conference=self.b_conference,
                b_title=self.b_title,
                performer__contact=self.performer.contact
                ).exclude(pk=self.pk).exists():
            raise ValidationError({
                NON_FIELD_ERRORS: [act_not_unique, ]
            })

    @property
    def profile(self):
        return self.performer.contact

    class Meta:
        app_label = "gbe"
        permissions = [
            ("assign_act",
             "Coordinate acts - assign status, book, and create for others"),
            ("review_act", "Can read other's acts and create reviews."),
        ]
