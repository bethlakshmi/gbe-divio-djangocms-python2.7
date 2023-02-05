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
    social_icons = {
        'Cash App': '<i class="fas fa-dollar-sign"></i>',
        'Facebook': '<i class="fab fa-facebook"></i>',
        'Instagram': '<i class="fab fa-instagram"></i>',
        'Paypal': '<i class="fab fa-paypal"></i>',
        'TikTok': '<i class="fab fa-tiktok"></i>',
        'Venmo': '<iconify-icon icon="simple-icons:velog"></iconify-icon>',
        'YouTube': '<i class="fab fa-youtube"></i>',
    }
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

    def get_url(self):
        if self.social_network in self.link_template:
            return self.link_template[self.social_network] + self.username
        return self.link

    def get_display_text(self):
        if self.social_network in self.link_template:
            return self.username
        return False

    def get_icon(self):
        if self.social_network in self.social_icons:
            return self.social_icons[self.social_network]
        return '<i class="fas fa-link"></i>'


    class Meta:
        ordering = ['performer', 'order']
        app_label = "gbe"
        unique_together = [['performer', 'order'], ]
