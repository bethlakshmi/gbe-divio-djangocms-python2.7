from django.db.models import (
    CharField,
    IntegerField,
    ManyToManyField,
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
    conference = ManyToManyField(Conference)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "gbe"
