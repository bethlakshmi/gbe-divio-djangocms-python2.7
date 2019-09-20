import pytz
from django.db.models import (
    ForeignKey,
    CharField,
    BooleanField,
    PositiveIntegerField,
    FileField,
    TextField,
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from settings import DATETIME_FORMAT
from django.utils.formats import date_format
from gbe.models import (
    Biddable,
    Persona,
    Profile,
    visible_bid_query
)

from gbetext import (
    acceptance_states,
    boolean_options,
)


class Costume(Biddable):
    '''
    An offer to display a costume at the Expo's costume display
      - profile is required, persona is optional
      - debut date is a text string to allow vague descriptions
      - act_title is optional, and therefore does not fit the rules of
        Biddable's title
    '''
    profile = ForeignKey(Profile, related_name="costumes")
    performer = ForeignKey(Persona, blank=True, null=True)
    creator = CharField(max_length=128)
    act_title = CharField(max_length=128, blank=True, null=True)
    debut_date = CharField(max_length=128, blank=True, null=True)
    active_use = BooleanField(choices=boolean_options, default=True)
    pieces = PositiveIntegerField(blank=True,
                                  null=True,
                                  validators=[MinValueValidator(1),
                                              MaxValueValidator(20)])
    pasties = BooleanField(choices=boolean_options, default=False)
    dress_size = PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)])
    more_info = TextField(blank=True)
    picture = FileField(upload_to="uploads/images", blank=True)

    @property
    def bidder_is_active(self):
        return self.profile.user_object.is_active

    @property
    def bid_review_header(self):
        return (['Performer (Creator)',
                 'Title',
                 'Act',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        name = ""
        if self.performer:
            name += self.performer.name + " "

        name += "(" + self.creator + ")"
        return [name,
                self.b_title,
                self.act_title,
                date_format(self.updated_at, "DATETIME_FORMAT"),
                acceptance_states[self.accepted][1]]

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    class Meta:
        app_label = "gbe"
