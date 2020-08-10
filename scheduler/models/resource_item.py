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
