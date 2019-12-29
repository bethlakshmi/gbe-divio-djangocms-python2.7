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

    send_daily_schedule = BooleanField(default=True)
    send_bid_notifications = BooleanField(default=True)
    send_role_notifications = BooleanField(default=True)
    send_schedule_change_notifications = BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'profile preferences'
        app_label = "gbe"
