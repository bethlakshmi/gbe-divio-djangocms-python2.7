import factory
from factory import (
    DjangoModelFactory,
    Sequence,
    SubFactory
)
import ticketing.models as tickets
import gbe.models as conf
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    UserFactory
)
from django.utils import timezone


class BrownPaperEventsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperEvents
    title = Sequence(lambda x: "title #%d" % x)
    description = "This is a desription"
    bpt_event_id = Sequence(lambda x: "%d" % x)
    conference = SubFactory(ConferenceFactory)
    primary = False
    act_submission_event = False
    vendor_submission_event = False
    include_conference = False
    include_most = False
    badgeable = False
    ticket_style = Sequence(lambda x: "BrownPaperEventTicketStyle #%d" % x)


class BrownPaperSettingsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.BrownPaperSettings
    developer_token = "devtoken"
    client_username = "clientusername"
    last_poll_time = timezone.now()


class TicketItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketItem
    bpt_event = SubFactory(BrownPaperEventsFactory)
    ticket_id = "111111-222222"
    title = Sequence(lambda x: "Ticket Item #%d" % x)
    cost = 99.99
    modified_by = "Ticket Item Mock"


class PurchaserFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Purchaser
    first_name = Sequence(lambda x: "purchaser_first: #%d" % x)
    last_name = Sequence(lambda x: "purchaser_last: #%d" % x)
    address = Sequence(lambda x: "purchaser_address: #%d" % x)
    city = "Boston"
    state = "MA"
    zip = "12312"
    country = "USA"
    email = Sequence(lambda x: "purchaser_%d@test.com" % x)
    phone = "111-222-3333"
    matched_to_user = SubFactory(UserFactory)


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.Transaction
    ticket_item = SubFactory(TicketItemFactory)
    purchaser = SubFactory(PurchaserFactory)
    amount = 99.99
    order_date = timezone.now()
    shipping_method = Sequence(lambda x: "shipping_method: #%d" % x)
    order_notes = Sequence(lambda x: "order_notes: #%d" % x)
    reference = Sequence(lambda x: "reference: #%d" % x)
    payment_source = Sequence(lambda x: "payment_source: #%d" % x)
    import_date = timezone.now()


class PayPalSettingsFactory(DjangoModelFactory):
    class Meta:
        model = tickets.PayPalSettings
    business_email = Sequence(lambda x: "%duser@email.com" % x)


class CheckListItemFactory(DjangoModelFactory):
    class Meta:
        model = tickets.CheckListItem
    description = Sequence(lambda x: "Check List Item: #%d" % x)


class TicketingEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)


class RoleEligibilityConditionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleEligibilityCondition

    checklistitem = SubFactory(CheckListItemFactory)
    role = "Teacher"


class TicketingExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.TicketingExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)

    @factory.post_generation
    def tickets(self, create, extracted, **kwargs):
        if extracted:
            # A list of groups were passed in, use them
            for ticket in extracted:
                self.tickets.add(ticket)


class RoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
    event = SubFactory(ClassFactory)


class NoEventRoleExclusionFactory(DjangoModelFactory):
    class Meta:
        model = tickets.RoleExclusion

    condition = SubFactory(RoleEligibilityConditionFactory)
    role = "Teacher"
