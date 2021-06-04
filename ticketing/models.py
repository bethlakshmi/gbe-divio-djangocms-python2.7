from django.db import models
from django.contrib.auth.models import User
from gbetext import (
    role_options,
    system_options,
)
from datetime import datetime


class BrownPaperSettings(models.Model):
    '''
    This class is used to hold basic settings for the interface with BPT.
    It should contain only one row and almost never changes.
    '''
    developer_token = models.CharField(max_length=15, primary_key=True)
    client_username = models.CharField(max_length=30)
    last_poll_time = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'Brown Paper Settings'


class EventbriteSettings(models.Model):
    '''
    if oath exists, the "sync" thread will first attempt to get org id
    if org id is present, then it will sync events & tickets & transactions
    automatically and/or on button click in ticketing
    '''
    oauth = models.CharField(max_length=128)
    organization_id = models.CharField(max_length=128, blank=True, null=True)
    system = models.IntegerField(choices=system_options, unique=True)

    class Meta:
        verbose_name_plural = 'Eventbrite Settings'


class PayPalSettings(models.Model):
    '''
    This class is used to hold basic settings sent to Paypal to identify
    payment.
    '''
    business_email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'PayPal Settings'


class TicketingEvents(models.Model):
    '''
    This class is used to hold the BPT event list.  It defines with Brown Paper
    Ticket Events should be queried to obtain information on the Ticket Items
    above.  This information mainly remains static - it is set up info for the
    interface with BPT.

      - include_conferece = if True this event provides tickets for all parts
            of the conference - Classes, Panels, Workshops - but not Master
            Classes, or Shows, or Special Events
      - include_most = includes everything EXCEPT Master Classes
    '''
    event_id = models.CharField(max_length=100, unique=True)
    act_submission_event = models.BooleanField(default=False,
                                               verbose_name='Act Fee')
    vendor_submission_event = models.BooleanField(default=False,
                                                  verbose_name='Vendor Fee')
    linked_events = models.ManyToManyField('gbe.Event',
                                           related_name='ticketing_item',
                                           blank=True)
    include_conference = models.BooleanField(default=False)
    include_most = models.BooleanField(default=False)
    badgeable = models.BooleanField(default=False)
    ticket_style = models.CharField(max_length=50, blank=True)
    conference = models.ForeignKey('gbe.Conference',
                                   on_delete=models.CASCADE,
                                   related_name='ticketing_item',
                                   blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    display_icon = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return "%s - %s" % (self.event_id, self.title)

    @property
    def visible(self):
        return self.ticketitems.filter(
            live=True,
            has_coupon=False).count() > 0

    @property
    def live_ticket_count(self):
        return TicketItem.objects.filter(
            ticketing_event=self,
            live=True,
            has_coupon=False).count()

    class Meta:
        verbose_name_plural = 'Ticketing Events'


class EventDetail(models.Model):
    detail = models.CharField(max_length=50, blank=True)
    ticketing_event = models.ForeignKey(TicketingEvents,
                                  on_delete=models.CASCADE,
                                  blank=True)


class TicketItem(models.Model):
    '''
    This class represents a type of ticket.  There is one ticket per price
    point, so an event like the Whole Shebang can have 10 or so different
    ticket - early bird, various discount codes, full price, etc.
      - active = whether the ticket should be actively displayed on the
          website.  Manually set
      - ticket_id = is calculated to conjoin event & ticket identifiers
    '''
    ticket_id = models.CharField(max_length=30)
    title = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=20, decimal_places=2)
    datestamp = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(max_length=30)
    ticketing_event = models.ForeignKey(TicketingEvents,
                                  on_delete=models.CASCADE,
                                  related_name="ticketitems",
                                  blank=True)
    live = models.BooleanField(default=False)
    add_on = models.BooleanField(default=False)
    has_coupon = models.BooleanField(default=False)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    is_minimum = models.BooleanField(default=False)

    def __str__(self):
        return '%s %s' % (self.ticket_id, self.title)

    @property
    def active(self):
        live_now = True
        if self.live and not self.has_coupon:
            if self.start_time and datetime.now() < self.start_time:
                live_now = False
            if self.end_time and datetime.now() > self.end_time:
                live_now = False
        else:
            live_now = False
        return live_now

    class Meta:
        ordering = ['cost']


class Purchaser(models.Model):
    '''
    This class is used to hold the information for a given person who has
    purchased a ticket.  It has all the information we can gather
    from BPT about the user.  It is meant to be mapped to a given User in
    our system, if we can.

    These are pretty much all char fields since we don't know the format of
    what BPT (or another system) will hand back.
    '''

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)

    # Note - if this is none, then we don't know who to match this purchase to
    # in our system.  This scenario will be pretty common.

    matched_to_user = models.ForeignKey(User,
                                        on_delete=models.CASCADE,
                                        default=None)

    def __str__(self):
        return "%s (%s)" % (self.email, str(self.matched_to_user))


class Transaction(models.Model):
    '''
    This class holds transaction records from an external source - in this
    case, Brown Paper Tickets.  Transactions are associated to a purchaser
    and a specific ticket item.
    '''

    ticket_item = models.ForeignKey(TicketItem, on_delete=models.CASCADE)
    purchaser = models.ForeignKey(Purchaser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    order_date = models.DateTimeField()
    shipping_method = models.CharField(max_length=50)
    order_notes = models.TextField()
    reference = models.CharField(max_length=30)
    payment_source = models.CharField(max_length=30)
    import_date = models.DateTimeField(auto_now=True)
    invoice = models.CharField(max_length=100, blank=True, null=True)
    custom = models.CharField(max_length=100, blank=True, null=True)

    def total_count(self):
        return Transaction.objects.filter(
            purchaser=self.purchaser, ticket_item=self.ticket_item).count()


class CheckListItem(models.Model):
    '''
    This is a physical item that we can give away at the registration desk
    Examples:  a badge, a wristband, a goodie bag, a guidebook, a release
    form, etc.  It may or may not be labeled for a specific users (for example,
    a badge has a name on it)
    '''
    description = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.description)


class EligibilityCondition(models.Model):
    '''
    This is the parent class connecting the conditions under which a
    CheckListItem can be given to the conditions themselves.

    Conditions are logically additive unless eliminated by exclusions.
    So if 3 conditions give an item with no exclusion, then the individual
    gets 3 items.

    TO Discuss (post expo) - consider making this abstract and using content
    types to link the exclusion foreign key to abstract cases of this class.
    '''
    checklistitem = models.ForeignKey(
        CheckListItem,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s")

    def is_excluded(self, held_tickets, profile, conference):
        is_excluded = False
        if held_tickets:
            for exclusion in self.ticketing_ticketingexclusion.all():
                if exclusion.is_excluded(held_tickets):
                    is_excluded = True

        if profile and not is_excluded:
            for exclusion in self.ticketing_roleexclusion.all():
                if exclusion.is_excluded(profile, conference):
                    is_excluded = True
        return is_excluded


class TicketingEligibilityCondition(EligibilityCondition):
    '''
    This is the implementation of the condition under which we give a
    checklist item to a purchaser because they have purchased a ticket
    Tickets are realized as BPT Events, the various tickets within an
    event do not qualify a user for anything more.

    Ticket conditions are additive.  X purchases = X items given to the
    buyer
    '''
    tickets = models.ManyToManyField(TicketItem,
                                     blank=False)

    def __str__(self):
        return ", ".join(str(tic) for tic in self.tickets.all())


class RoleEligibilityCondition(EligibilityCondition):
    '''
    This is the implementation of the condition under which we give a
    checklist item to a person because they fulfill an assigned role.

    Roles are given once per person per conference - being a role
    gets exactly 1 of the item.
    '''
    role = models.CharField(max_length=25,
                            choices=role_options)

    def __str__(self):
        return str(self.role)


class Exclusion(models.Model):
    '''
    This is the abstract class connecting the cases under which a
    CheckListItem should be assigned, even when it meets the current
    condition.  Exclusions are combined in many to 1 conditions as
    logical OR cases - any case being true negates the condition.
    '''
    condition = models.ForeignKey(
        EligibilityCondition,
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s")

    class Meta:
        abstract = True


class TicketingExclusion(Exclusion):
    '''
    This is the implementation of the case when the presence of a ticket
    purchase eliminates the eligibility of the individual for getting the
    checklist item under the given condition.  The usual case is that a
    person purchased a ticket that includes an equivalent to the current
    item and maybe more.
    '''
    tickets = models.ManyToManyField(TicketItem,
                                     blank=False)

    def __str__(self):
        return ", ".join(str(tic) for tic in self.tickets.all())

    def is_excluded(self, held_tickets):
        '''
        Return True if the referenced condition should be excluded from the
        participant's package.  This is true when there is a match between the
        held tickets and the tickets for the exclusion
        '''
        is_excluded = False
        for ticket in held_tickets:
            if ticket in self.tickets.all():
                is_excluded = True

        return is_excluded


class RoleExclusion(Exclusion):
    '''
    This is the implementation of the case under which we don't give a ticket
    because of the event that the person is participating in.  This is largely
    because we know the person will not be able to participate in an event
    they are contributing to - for example a performer in a show.

    If no event, then the implication is that being this role for ANY event
    means the exclusion takes effect
    '''
    role = models.CharField(max_length=25,
                            choices=role_options)
    event = models.ForeignKey('gbe.Event',
                              on_delete=models.CASCADE,
                              blank=True,
                              null=True)

    def __str__(self):
        describe = self.role
        if self.event:
            describe += ", " + str(self.event)
        return str(describe)

    def is_excluded(self, profile, conference):
        '''
        Return True if the referenced condition should be excluded from the
        participant's package.  This is true when there is a match between the
        user's profile and the referenced event
        '''
        is_excluded = False
        if not self.event:
            is_excluded = self.role in profile.get_roles(conference)
        else:
            is_excluded = profile.has_role_in_event(self.role, self.event)
        return is_excluded
