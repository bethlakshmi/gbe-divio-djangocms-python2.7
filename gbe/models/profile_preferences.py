from django.db.models import (
    CASCADE,
    Model,
    OneToOneField,
    CharField,
    TextField,
    BooleanField,
)
from gbe.models import Account
from gbetext import yes_no_maybe_options


class ProfilePreferences(Model):
    '''
    User-settable preferences controlling interaction with the
    Expo and with the site.
    '''
    account = OneToOneField(Account,
                            on_delete=CASCADE,
                            related_name='preferences',
                            null=True)
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
