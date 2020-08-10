from model_utils.managers import InheritanceManager
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
)
from scheduler.models import (
    ActItem,
    Resource,
)


class ActResource(Resource):
    '''
    A schedulable object wrapping an Act
    '''
    objects = InheritanceManager()
    _item = ForeignKey(ActItem, on_delete=CASCADE)
    role = CharField(max_length=50, blank=True)

    @property
    def order(self):
        for alloc in self.allocations.all():
            if hasattr(alloc, 'ordering'):
                return alloc.ordering.order

    @property
    def type(self):
        return "Act"

    def __str__(self):
        try:
            return self.item.describe
        except:
            return "No Act Item"
