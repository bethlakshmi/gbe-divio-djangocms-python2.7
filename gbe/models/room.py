from django.db.models import (
    CharField,
    IntegerField,
)
from scheduler.models import LocationItem


class Room(LocationItem):
    '''
    A room at the expo center
    '''
    name = CharField(max_length=50)
    capacity = IntegerField()
    overbook_size = IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        app_label = "gbe"
