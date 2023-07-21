from django.db.models import (
    CASCADE,
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
                            on_delete=CASCADE,
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

    @property
    def inform_about_list(self):
        if self.inform_about:
            return eval(self.inform_about)
        else:
            return "None"

    class Meta:
        verbose_name_plural = 'profile preferences'
        app_label = "gbe"
