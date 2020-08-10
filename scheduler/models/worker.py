from model_utils.managers import InheritanceManager
from scheduler.models import (
    Resource,
    WorkerItem,
)
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
)
from gbetext import role_options


class Worker(Resource):
    '''
    objects = InheritanceManager()
    An allocatable person
    '''
    _item = ForeignKey(WorkerItem, on_delete=CASCADE)
    role = CharField(max_length=50, choices=role_options, blank=True)

    @property
    def workeritem(self):
        return WorkerItem.objects.get_subclass(
            resourceitem_id=self._item.resourceitem_id)

    @property
    def type(self):
        return self.role

    def __str__(self):
        return self.item.describe
