from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    PayPalSettingsFactory,
    TicketItemFactory,
)
from django.contrib.auth.models import User
from tests.factories.gbe_factories import UserFactory
from django.core.files import File
from filer.models.filemodels import File as FilerFile


def setup_fees(conference, is_act=False, is_vendor=False):
    PayPalSettingsFactory()
    event = TicketingEventsFactory(conference=conference,
                                   vendor_submission_event=is_vendor,
                                   act_submission_event=is_act)
    if is_vendor:
        ticket = TicketItemFactory(live=True, ticketing_event=event)
        add_on = TicketItemFactory(live=True,
                                   ticketing_event=event,
                                   add_on=True)
        return [ticket, add_on]
    if is_act:
        ticket = TicketItemFactory(live=True,
                                   ticketing_event=event,
                                   is_minimum=True,
                                   cost=10)
        return [ticket]


def set_form():
    if User.objects.filter(username='superuser_for_test').exists():
        superuser = User.objects.get(username='superuser_for_test')
    else:
        superuser = UserFactory(
            username='superuser_for_test',
            email='admin@importpdf.com',
            password='secret',
            is_staff=True,
            is_superuser=True)

    path = "tests/ticketing/dumb_pdf.pdf"
    current_pdf = FilerFile.objects.create(
        owner=superuser,
        original_filename="dumb_pdf.png",
        file=File(open(path, 'rb')))
    current_pdf.save()

    return current_pdf
