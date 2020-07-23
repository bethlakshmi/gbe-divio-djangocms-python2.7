from model_utils.managers import InheritanceManager
from django.db.models import Model


class Schedulable(Model):
    '''
    Interface for an item that can appear on a conference schedule - either an
    event or a resource allocation. (resource allocations can include, eg,
    volunteer commitments for a particular person, or for a particular event,
    or for a block of time - so this is a pretty flexible idea)
    Note that conference models should NEVER inherit this directly or
    indirectly.
    This is why we use the indirection model: we don't want to store scheduler
    data in the conference model.
    '''
    objects = InheritanceManager()

    @property
    def start_time(self):
        try:
            return self.starttime
        except:
            return None

    @property
    def end_time(self):
        return self.starttime + self.duration

    class Meta:
        abstract = True
