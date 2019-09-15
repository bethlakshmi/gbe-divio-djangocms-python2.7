from model_utils.managers import InheritanceManager

from django.db.models import (
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
    contact = ForeignKey(Profile, related_name='contact')
    name = CharField(max_length=100,     # How this Performer is listed
                     unique=True)        # in a playbill.
    homepage = URLField(blank=True)
    bio = TextField()
    experience = PositiveIntegerField()       # in years
    awards = TextField(blank=True)
    img = FilerImageField(
        null=True,
        related_name="image_performer")
    festivals = TextField(blank=True)     # placeholder only

    def get_schedule(self):
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_schedule()

    def get_profiles(self):
        '''
        Gets all of the people performing in the act
        '''
        return Performer.objects.get_subclass(
            resourceitem_id=self.resourceitem_id).get_profiles()

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
    def complete(self):
        return True

    @property
    def describe(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']
        app_label = "gbe"
