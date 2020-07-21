from django.db.models import (
    CASCADE,
    IntegerField,
    Model,
    OneToOneField,
)
from scheduler.models import ResourceAllocation


class Ordering(Model):
    '''
    A decorator for Allocations to allow representation of orderings
    Attaches to an Allocation. No effort is made to ensure uniqueness or
    completeness of an ordering, this is handled later in the business
    logic.
    Orderings are assumed to sort from low to high. Negative ordering
    indices are allowed.
    '''
    order = IntegerField(default=0)
    allocation = OneToOneField(ResourceAllocation, on_delete=CASCADE)
