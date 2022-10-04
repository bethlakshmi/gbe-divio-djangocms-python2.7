from model_utils.managers import InheritanceManager
from django.db.models import (
    CASCADE,
    ForeignKey,
    CharField,
    PositiveIntegerField,
    TextField,
    URLField,
)
from gbe.models import Profile
from scheduler.models import WorkerItem
from filer.fields.image import FilerImageField


class Performer (WorkerItem):
    '''
    Abstract base class for any solo, group, or troupe - anything that
    can appear in a show lineup or teach a class
    The fields are named as we would name them for a single performer.
    In all cases, when applied to an aggregate (group or troup) they
    apply to the aggregate as a whole. The Boston Baby Dolls DO NOT
    list awards won by members of the troupe, only those won by the
    troup. (individuals can list their own, and these can roll up if
    we want). Likewise, the bio of the Baby Dolls is the bio of the
    company, not of the members, and so forth.
    '''
    objects = InheritanceManager()
    contact = ForeignKey(Profile,
                         on_delete=CASCADE,
                         related_name='contact')
    name = CharField(max_length=100)
    label = CharField(max_length=100, blank=True)
    homepage = URLField(blank=True)
    bio = TextField()
    experience = PositiveIntegerField(null=True)
    year_started = PositiveIntegerField(null=True)
    awards = TextField(blank=True)
    img = FilerImageField(
        on_delete=CASCADE,
        null=True,
        related_name="image_performer")
    festivals = TextField(blank=True)     # placeholder only

    def get_profiles(self):
        '''
        Gets all of the people performing in the act
        '''
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_profiles()

    def has_bids(self):
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).has_bids()

    @property
    def is_active(self):
        return self.contact.user_object.is_active

    @property
    def user_object(self):
        return self.contact.user_object

    @property
    def contact_email(self):
        return self.contact.user_object.email

    @property
    def describe(self):
        return self.name

    def __str__(self):
        perf_string = self.name
        if self.label and len(self.label) > 0:
            perf_string = "%s - %s" % (self.name, self.label)
        return perf_string

    class Meta:
        ordering = ['name']
        app_label = "gbe"
        unique_together = [['name', 'label']]
