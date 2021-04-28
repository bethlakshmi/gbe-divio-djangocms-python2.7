import pytz
from settings import GBE_TABLE_FORMAT
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    FileField,
    ForeignKey,
    TextField,
    URLField,
)
from gbe.models import (
    Biddable,
    Business,
    Profile,
    visible_bid_query
)
from gbetext import (
    acceptance_states,
    boolean_options,
)
from gbe_forms_text import (
    vendor_schedule_options,
    vendor_featured_options,
)
from filer.fields.image import FilerImageField


class Vendor(Biddable):
    '''
    A request for space in the Expo marketplace.
    Note that company name is stored in the title field inherited
    from Biddable, and description is also inherited
    '''
    business = ForeignKey(Business, on_delete=CASCADE)
    want_help = BooleanField(choices=boolean_options,
                             blank=True,
                             default=False)
    help_description = TextField(blank=True)
    help_times = TextField(blank=True)
    level = CharField(max_length=128,
                      choices=vendor_featured_options,
                      blank=True,
                      default='')

    def __str__(self):
        return self.b_title  # "title" here is company name

    def clone(self):
        vendor = Vendor(business=self.business,
                        want_help=self.want_help,
                        help_description=self.help_description,
                        help_times=self.help_times,
                        b_title=self.b_title,
                        b_description=self.b_description,
                        b_conference=Conference.objects.filter(
                            status="upcoming").first())

        vendor.save()
        return vendor

    @property
    def bidder_is_active(self):
        active = False
        for owner in self.business.owners:
            if owner.user_object.is_active:
                active = True
        return active

    @property
    def bid_review_header(self):
        return (['Bidder',
                 'Business Name',
                 'Website',
                 'Last Update',
                 'State',
                 'Reviews',
                 'Action'])

    @property
    def bid_review_summary(self):
        acceptance = acceptance_states[self.accepted][1]
        if self.level:
            acceptance = "%s, %s" % (acceptance_states[self.accepted][1],
                                     self.level)
        return [self.business.owners.filter(
                    user_object__is_active=True).display_name,
                self.business.name,
                self.business.website,
                self.updated_at.strftime(GBE_TABLE_FORMAT),
                acceptance]

    @property
    def bids_to_review(self):
        return type(self).objects.filter(
            visible_bid_query,
            submitted=True,
            accepted=0)

    @property
    def get_help_times_display(self):
        choices = []
        for choice in vendor_schedule_options:
            if choice[0] in self.help_times:
                choices += [choice[1]]
        return choices

    class Meta:
        app_label = "gbe"
