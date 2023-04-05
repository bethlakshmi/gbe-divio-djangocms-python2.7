from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    TextField,
)
from published.models import PublishedModel
from published.constants import *
from gbetext import acceptance_states
from model_utils.managers import InheritanceManager
from gbe.models import Profile
from settings import GBE_DATETIME_FORMAT


class Article(PublishedModel):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    title = CharField(max_length=128)
    summary = CharField(max_length=300)
    description = TextField(blank=True)
    creator = ForeignKey(Profile, on_delete=CASCADE)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        app_label = "gbe"

    def __str__(self):
        return self.title

    def published_date(self):
        published_date = self.created_at
        if self.publish_status == AVAILABLE_AFTER:
            published_date = self.live_as_of
        return published_date.strftime(GBE_DATETIME_FORMAT)
