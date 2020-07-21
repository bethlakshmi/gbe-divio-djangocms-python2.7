from model_utils.managers import InheritanceManager
from django.db.models import (
    AutoField,
    Model,
)


class ResourceItem(Model):
    '''
    The payload for a resource
    '''
    objects = InheritanceManager()
    resourceitem_id = AutoField(primary_key=True)

    @property
    def describe(self):
        child = ResourceItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id)
        return child.__class__.__name__ + ":  " + child.describe

    def __str__(self):
        return str(self.describe)
