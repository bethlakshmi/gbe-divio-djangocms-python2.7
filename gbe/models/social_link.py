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


class SocialLink(Model):
    social_options = [
        ('Cash App', 'Cash App'),
        ('Facebook', 'Facebook'),
        ('Instagram', 'Instagram'),
        ('Paypal', 'Paypal'),
        ('TikTok', 'TikTok'),
        ('Venmo', 'Venmo'),
        ('Website', 'Website'),
        ('YouTube', 'YouTube'),
    ]
    link_template = {
        'Cash App': 'Cash App',
        'Instagram': 'Instagram',
        'Paypal': 'Paypal',
        'TikTok': 'TikTok',
        'Venmo': 'Venmo',
        'YouTube': 'YouTube',
    }
    performer = ForeignKey(Performer,
                           on_delete=CASCADE,
                           related_name='links')
    link = URLField(null=True, blank=True)
    username = CharField(null=True, blank=True, max_length=100)
    social_network = CharField(max_length=40,
                              choices=social_options,
                              blank=True)
    order = PositiveIntegerField(validators=[MinValueValidator(1),
                                             MaxValueValidator(5)])

    class Meta:
        ordering = ['performer', 'order']
        app_label = "gbe"
        unique_together = [['social_network', 'link'],
                           ['social_network', 'username']]
