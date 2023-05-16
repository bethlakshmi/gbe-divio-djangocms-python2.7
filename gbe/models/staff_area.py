from django.db.models import (
    CASCADE,
    CharField,
    TextField,
    ForeignKey,
    IntegerField,
    Model,
    SlugField,
)
from gbe.models import (
    Account,
    Conference,
    Profile,
    Room,
)


class StaffArea(Model):
    '''
    This is a major area w/in the expo. It is a kind of a container for
    Events, but one with a specified leader, which makes it a kind of
    privilege as well.
    '''
    title = CharField(max_length=128)
    slug = SlugField()
    description = TextField()
    conference = ForeignKey(
        Conference,
        on_delete=CASCADE)
    default_location = ForeignKey(Room,
                                  on_delete=CASCADE,
                                  blank=True,
                                  null=True)
    default_volunteers = IntegerField(default="1",
                                      blank=True,
                                      null=True)
    staff_lead = ForeignKey(Profile,
                            on_delete=CASCADE,
                            blank=True,
                            null=True)
    staff_lead_account = ForeignKey(Account,
                                    on_delete=CASCADE,
                                    blank=True,
                                    null=True)
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['conference', 'title']
        app_label = "gbe"
        unique_together = (('title', 'conference'), ('slug', 'conference'))
