from model_utils.managers import InheritanceManager
from django.db.models import (
    CASCADE,
    ForeignKey,
)
from scheduler.models import (
    LocationItem,
    Resource,
)


class Location(Resource):
    '''
    A resource which is a location.
    '''
    objects = InheritanceManager()
    _item = ForeignKey(LocationItem, on_delete=CASCADE)

    @property
    def type(self):
        return "location"

    def __str__(self):
        try:
            return self.item.describe
        except:
            return "No Location Item"
