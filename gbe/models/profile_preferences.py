from django.db.models import (
    Model,
    OneToOneField,
    CharField,
    TextField,
    BooleanField,
)
from gbe.models import Profile
from gbetext import yes_no_maybe_options


class ProfilePreferences(Model):
    '''
    User-settable preferences controlling interaction with the
    Expo and with the site.
    '''
    profile = OneToOneField(Profile,
                            related_name='preferences')
    in_hotel = CharField(max_length=10,
                         blank=True,
                         choices=yes_no_maybe_options)
    inform_about = TextField(blank=True)
    show_hotel_infobox = BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'profile preferences'
        app_label = "gbe"
