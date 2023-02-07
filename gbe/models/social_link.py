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
        'Cash App': 'https://cash.app/$',
        'Instagram': 'https://www.instagram.com/',
        'Paypal': 'https://paypal.me/',
        'TikTok': 'https://www.tiktok.com/@',
        'Venmo': 'https://venmo.com/',
        'YouTube': 'https://www.youtube.com/c/',
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
