from django.contrib.auth.models import User
from django.db.models import (
    CharField,
    IntegerField,
    ManyToManyField,
    Model,
    TextField,
)
from gbetext import role_options


class People(Model):
    '''
    A person or set of people who are scheduled together
    '''
    users = ManyToManyField(User)
    role = CharField(max_length=50, choices=role_options, blank=True)
    label = TextField(default='')
    class_name = CharField(max_length=50, blank=True)
    class_id = IntegerField(blank=True, null=True)


    class Meta:
        app_label = "scheduler"
        unique_together = (('class_name', 'class_id'),)
