from model_utils.managers import InheritanceManager
from django.db.models import Model


class Resource(Model):
    '''
    A person, place, or thing that can be allocated for an event.
    A resource has a payload and properties derived from that payload.
    This is basically a tag interface, allowing us to select all resources.
    '''
    objects = InheritanceManager()

    @property
    def type(self):
        child = Resource.objects.get_subclass(id=self.id)
        if child.__class__.__name__ != "Resource":
            return child.type
        else:
            return "Resource (no child)"

    @property
    def item(self):
        child = Resource.objects.get_subclass(id=self.id)
        return child._item

    @property
    def as_subtype(self):
        child = Resource.objects.get_subclass(id=self.id)
        return child

    def __str__(self):
        allocated_resource = Resource.objects.get_subclass(id=self.id)
        if allocated_resource.__class__.__name__ != "Resource":
            return str(allocated_resource)
        else:
            return "Error in resource allocation, no resource"

    class Meta:
        app_label = "scheduler"
