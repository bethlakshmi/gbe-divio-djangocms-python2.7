import pytz
from settings import GBE_TABLE_FORMAT
from django.db.models import (
    ForeignKey,
    CASCADE,
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
from gbe.models import (
    Biddable,
    Bio,
    Profile,
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
    profile = ForeignKey(Profile,
                         on_delete=CASCADE,
                         related_name="costumes")
    bio = ForeignKey(Bio,
                     on_delete=CASCADE,
                     blank=True,
                     null=True)
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
        if self.bio:
            name += self.bio.name + " "

        name += "(" + self.creator + ")"
        return [name,
                self.b_title,
                self.act_title,
                self.updated_at.strftime(GBE_TABLE_FORMAT),
                acceptance_states[self.accepted][1]]

    class Meta:
        app_label = "gbe"
