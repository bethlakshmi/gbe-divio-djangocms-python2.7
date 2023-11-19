from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    ManyToManyField,
    Model,
    TextField,
    URLField,
)
from gbe.models import Profile
from filer.fields.image import FilerImageField


class Business(Model):
    '''
    A request for space in the Expo marketplace.
    Note that company name is stored in the title field inherited
    from Biddable, and description is also inherited
    '''
    name = CharField(max_length=128)
    description = TextField(blank=True)
    owners = ManyToManyField(Profile)
    website = URLField(blank=True)
    physical_address = TextField()
    publish_physical_address = BooleanField(default=False)
    img = FilerImageField(
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="image_business")

    def show_owners(self, active_only=True):
        owners = ""
        for owner in self.owners.filter(user_object__is_active=True):
            owners = "%s, %s" % (owner, owners)
        if not active_only:
            for owner in self.owners.filter(user_object__is_active=False):
                owners = "%s (inactive), %s" % (owner, owners)
        return owners.strip()[:-1]

    @property
    def active_owners(self):
        return self.owners.filter(user_object__is_active=True)

    def __str__(self):
        return self.name  # "title" here is company name

    class Meta:
        app_label = "gbe"
        unique_together = [['name', 'website']]
        verbose_name_plural = 'businesses'
        ordering = ["name", ]
