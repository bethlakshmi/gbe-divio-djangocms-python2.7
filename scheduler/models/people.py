from django.contrib.auth.models import User
from django.db.models import (
    CharField,
    IntegerField,
    ManyToManyField,
    Model,
)


class People(Model):
    '''
    A person or set of people who are scheduled together
    These are 1:1 to the profiles + the bios (troupe and solo)
    '''
    users = ManyToManyField(User)
    class_name = CharField(max_length=50, blank=True)
    class_id = IntegerField(blank=True, null=True)
    commitment_class_name = CharField(max_length=50, blank=True)
    commitment_class_id = IntegerField(blank=True, null=True)

    class Meta:
        app_label = "scheduler"
        unique_together = (('class_name',
                            'class_id',
                            'commitment_class_name',
                            'commitment_class_id'),)
