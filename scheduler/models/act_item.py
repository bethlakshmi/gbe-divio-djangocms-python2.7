from model_utils.managers import InheritanceManager
from scheduler.models import ResourceItem


class ActItem(ResourceItem):
    '''
    Payload object for an Act
    '''
    objects = InheritanceManager()
