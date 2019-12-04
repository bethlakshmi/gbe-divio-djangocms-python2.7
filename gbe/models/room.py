from django.db.models import (
    CharField,
    IntegerField,
    ManyToManyField,
    TextField,
)
from scheduler.models import LocationItem
from gbe.models import Conference


class Room(LocationItem):
    '''
    A room at the expo center
    '''
    name = CharField(max_length=50)
    capacity = IntegerField()
    overbook_size = IntegerField()
    conferences = ManyToManyField(Conference)
    address = TextField(
        max_length=500,
        blank=True,
        help_text="This can include HTML, and it will be for formatting.")
    map_embed = TextField(
        max_length=1000, 
        blank=True,
        help_text="Use the embedded map instructions and this will display " +
        "on event pages.  With Google, small size is recommended.")

    def __str__(self):
        return self.name

    class Meta:
        app_label = "gbe"
