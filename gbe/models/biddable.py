from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    Model,
    TextField,
)
from gbe.models import Conference
from gbetext import acceptance_states
from model_utils.managers import InheritanceManager


class Biddable(Model):
    '''
    Abstract base class for items which can be Bid
    Essentially, specifies that we want something with a title
    '''
    objects = InheritanceManager()
    b_title = CharField(max_length=128)
    b_description = TextField(blank=True)
    submitted = BooleanField(default=False)
    accepted = IntegerField(choices=acceptance_states,
                            default=0,
                            blank=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    b_conference = ForeignKey(
        Conference,
        on_delete=CASCADE,
        related_name="b_conference_set",
        blank=True,
        null=True)

    class Meta:
        verbose_name = "biddable item"
        verbose_name_plural = "biddable items"
        app_label = "gbe"

    def __str__(self):
        return self.b_title

    @property
    def ready_for_review(self):
        return (self.submitted and
                self.accepted == 0)

    @property
    def is_current(self):
        return self.b_conference.status in ("upcoming", "ongoing")

    @property
    def bidder_is_active(self):
        active = False
        for profile in self.profiles:
            if profile.user_object.is_active:
                active = True
        return active

    @property
    def profiles(self):
        return [Biddable.objects.get_subclass(pk=self.pk).profile]
