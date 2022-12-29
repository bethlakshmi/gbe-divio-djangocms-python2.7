from model_utils.managers import InheritanceManager
from django.db.models import (
    CASCADE,
    CharField,
    ForeignKey,
    Model,
    PositiveIntegerField,
    URLField,
)
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator
)
from gbe.models import Performer
from gbetext import social_options

class SocialLink(Model):
    performer = ForeignKey(Performer,
                           on_delete=CASCADE,
                           related_name='links')
    link = URLField(null=True)
    username = CharField(null=True, max_length=100)
    socal_network = CharField(max_length=5,
                              choices=social_options,
                              blank=True)
    order = PositiveIntegerField(validators=[MinValueValidator(0),
                                             MaxValueValidator(4)])

    class Meta:
        ordering = ['performer', 'order']
        app_label = "gbe"
        unique_together = [['socal_network', 'link']]
