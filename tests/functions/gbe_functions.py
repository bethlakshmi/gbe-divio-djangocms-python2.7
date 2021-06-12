from gbe.models import (
    Conference,
    Profile,
)
from django.contrib.auth.models import (
    Group,
    User,
)
from tests.factories.gbe_factories import (
    ActFactory,
    ConferenceFactory,
)

from tests.factories.ticketing_factories import (
    TicketingEventsFactory,
    TransactionFactory,
    TicketItemFactory,
    PurchaserFactory,
)
from post_office.models import (
    Email,
    EmailTemplate
)
from django.core import mail
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from filer.models.imagemodels import Image
from filer.models.foldermodels import Folder
from settings import DEFAULT_FROM_EMAIL


def _user_for(user_or_profile):
    if type(user_or_profile) == Profile:
        user = user_or_profile.user_object
    elif type(user_or_profile) == User:
        user = user_or_profile
    else:
        raise ValueError("this function requires a Profile or User")
    return user


def login_as(user_or_profile, testcase):
    user = _user_for(user_or_profile)
    user.set_password('foo')
    user.save()
    testcase.client.login(username=user.username,
                          email=user.email,
                          password='foo')


def grant_privilege(user_or_profile, privilege):
    '''Add named privilege to user's groups. If group does not exist, create it
    '''
    user = _user_for(user_or_profile)
    g, _ = Group.objects.get_or_create(name=privilege)
    if g in user.groups.all():
        return
    else:
        user.groups.add(g)


def is_login_page(response):
    return b'I forgot my username or password!' in response.content


def current_conference():
    current_confs = Conference.objects.filter(
        status__in=('upcoming', 'ongoing'),
        accepting_bids=True)
    if current_confs.exists():
        return current_confs.first()
    return ConferenceFactory(status='upcoming',
                             accepting_bids=True)


def clear_conferences():
    Conference.objects.all().delete()


def assert_alert_exists(response, tag, label, text):
    alert_html = '<div class="alert gbe-alert-%s">\n' + \
        '          <a href="#" class="close" data-dismiss="alert" ' + \
        'aria-label="close">&times;</a>\n' + \
        '          <strong>%s:</strong> %s\n' \
        '	</div>'
    assert bytes(alert_html % (tag, label, text), 'utf-8') in response.content


def assert_option_state(response, value, text, selected=False):
    selected_state = ""
    if selected:
        selected_state = " selected"
    option_state = (
        '<option value="%s"%s>%s</option>' % (
                    value, selected_state, text))
    assert bytes(option_state, 'utf-8') in response.content


def assert_email_template_create(
        template_name,
        expected_subject):
    assert 1 == len(mail.outbox)
    msg = mail.outbox[0]
    assert msg.subject == expected_subject
    template = EmailTemplate.objects.get(name=template_name)
    assert template.subject == expected_subject
    assert template.sender.from_email == settings.DEFAULT_FROM_EMAIL


def assert_email_template_used(
        expected_subject,
        email=settings.DEFAULT_FROM_EMAIL,
        outbox_size=1,
        message_index=0):
    assert outbox_size == len(mail.outbox)
    msg = mail.outbox[message_index]
    assert msg.subject == expected_subject
    header = {'Reply-to': email}
    assert msg.extra_headers == header
    return msg


def assert_email_recipient(to_list, outbox_size=1, message_index=0):
    assert outbox_size == len(mail.outbox)
    msg = mail.outbox[message_index]
    for to_msg, to_test in zip(msg.to, to_list):
        assert to_msg == to_test


def assert_email_contents(contents):
    assert 1 == len(mail.outbox)
    msg = mail.outbox[0]
    assert contents in msg.body


def assert_right_mail_right_addresses(
        queue_order,
        num_email,
        expected_subject,
        to_email_array,
        from_email=settings.DEFAULT_FROM_EMAIL):
    header = {'Reply-to': from_email}
    assert num_email == len(mail.outbox)
    msg = mail.outbox[queue_order]
    assert msg.subject == expected_subject
    assert msg.to == to_email_array
    assert msg.extra_headers == header
    return msg


def assert_queued_email(to_list, subject, message, sender, extras=[]):
    queued_email = Email.objects.filter(
        status=2,
        subject=subject,
        html_message__startswith=message,
        headers={'Reply-to': sender},
        from_email=DEFAULT_FROM_EMAIL
        )
    for recipient in to_list:
        assert queued_email.filter(to=recipient).exists()
        match = queued_email.filter(to=recipient).first()
        for extra in extras:
            assert extra in match.html_message


def make_act_app_purchase(conference, user_object):
    purchaser = PurchaserFactory(
        matched_to_user=user_object)
    transaction = TransactionFactory(purchaser=purchaser)
    transaction.ticket_item.ticketing_event.conference = conference
    transaction.ticket_item.ticketing_event.act_submission_event = True
    transaction.ticket_item.ticketing_event.save()
    return transaction


def make_act_app_ticket(conference):
    ticketing_event = TicketingEventsFactory(conference=conference,
                                             act_submission_event=True)
    ticket_id = "%s-1111" % (ticketing_event.event_id)
    ticket = TicketItemFactory(ticket_id=ticket_id)
    return ticketing_event.event_id


def post_act_conflict(conference, performer, data, url, testcase):
    original = ActFactory(
        b_conference=conference,
        performer=performer)
    login_as(performer.performer_profile, testcase)
    data['theact-b_title'] = original.b_title
    data['theact-b_conference'] = conference.pk
    response = testcase.client.post(
        url,
        data=data,
        follow=True)
    return response, original


def make_vendor_app_purchase(conference, user_object):
    ticketing_event = TicketingEventsFactory(conference=conference,
                                             vendor_submission_event=True)
    purchaser = PurchaserFactory(matched_to_user=user_object)
    ticket_id = "%s-1111" % (ticketing_event.event_id)
    ticket = TicketItemFactory(ticket_id=ticket_id,
                               ticketing_event=ticketing_event)
    transaction = TransactionFactory(ticket_item=ticket,
                                     purchaser=purchaser)
    return transaction


def make_vendor_app_ticket(conference):
    ticketing_event = TicketingEventsFactory(conference=conference,
                                             vendor_submission_event=True)
    ticket_id = "%s-1111" % (ticketing_event.event_id)
    ticket = TicketItemFactory(ticket_id=ticket_id)
    return ticketing_event.event_id


def make_admission_purchase(conference,
                            user_object,
                            include_most=False,
                            include_conference=False):
    ticketing_event = TicketingEventsFactory(
        conference=conference,
        include_most=include_most,
        include_conference=include_conference)
    purchaser = PurchaserFactory(matched_to_user=user_object)
    ticket_id = "%s-1111" % (ticketing_event.event_id)
    ticket = TicketItemFactory(ticket_id=ticket_id,
                               ticketing_event=ticketing_event)
    transaction = TransactionFactory(ticket_item=ticket,
                                     purchaser=purchaser)


def bad_id_for(cls):
    objects = cls.objects.all()
    if objects.exists():
        return objects.latest('pk').pk + 1
    return 1


def set_image(item=None, folder_name=None):
    folder = None
    if User.objects.filter(username='superuser_for_test').exists():
        superuser = User.objects.get(username='superuser_for_test')
    else:
        superuser = User.objects.create_superuser(
            'superuser_for_test',
            'admin@importimage.com',
            'secret')
    if folder_name:
        folder, created = Folder.objects.get_or_create(
            name=folder_name)
    path = "tests/gbe/gbe_pagebanner.png"
    current_img = Image.objects.create(
        folder=folder,
        owner=superuser,
        original_filename="gbe_pagebanner.png",
        file=File(open(path, 'rb')))
    current_img.save()
    if item:
        item.img_id = current_img.pk
        item.save()
    return current_img
