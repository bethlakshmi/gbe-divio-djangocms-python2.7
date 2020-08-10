from model_utils.managers import InheritanceManager
from scheduler.models import ResourceItem


class ActItem(ResourceItem):
    '''
    Payload object for an Act
    '''
    objects = InheritanceManager()

    @property
    def as_subtype(self):
        return self.act

    @property
    def bio(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).bio

    @property
    def describe(self):
        return ActItem.objects.get_subclass(
            resourceitem_id=self.resourceitem_id
        ).b_title
