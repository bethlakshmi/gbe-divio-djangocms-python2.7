from django.db.models import (
    SET_NULL,
    CharField,
    DateTimeField,
    ForeignKey,
    SlugField,
    TextField,
)
from django.urls import reverse
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
    summary = CharField(max_length=300, blank=True)
    content = TextField()
    creator = ForeignKey(Profile,
                         on_delete=SET_NULL,
                         null=True,
                         blank=True)
    slug = SlugField(null=False, unique=True)

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

    def get_absolute_url(self):
        return reverse("gbe:news_item", kwargs={"slug": self.slug})
