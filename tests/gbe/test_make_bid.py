from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import (
    ConferenceFactory,
    EmailTemplateSenderFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import (
    assert_right_mail_right_addresses,
    grant_privilege,
    login_as,
)
from gbe.models import (
    Conference,
)
from post_office.models import EmailTemplate


class TestMakeBid(TestCase):
    '''Tests for the centralized make bid view'''
    view_name = 'class_create'

    def setUp(self):
        Conference.objects.all().delete()
        self.client = Client()
        self.performer = PersonaFactory()
        self.conference = ConferenceFactory(accepting_bids=True)

    def test_bid_no_profile(self):
        '''act_bid, when user has no profile, should bounce out to /profile'''
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        user = UserFactory()
        login_as(user, self)
        response = self.client.get(url, )
        self.assertRedirects(
            response,
            '%s?next=%s' % (
                reverse('profile_update', urlconf='gbe.urls'),
                reverse('class_create', urlconf='gbe.urls')))

    def test_get_new_bid(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.conference.conference_name in response.content)

    def test_volunteer_conflict_sends_notification_w_bid_details(self):
        privileged_profile = ProfileFactory()
        grant_privilege(
            privileged_profile.user_object,
            'Class Reviewers')
        EmailTemplate.objects.all().delete()
        subject_format = "bidder: %s, bid: %s"
        EmailTemplateSenderFactory(
            from_email="class@notify.com",
            template__name='class submission notification',
            template__subject="bidder: %s, bid: %s" % (
                "{{ bidder }}",
                "{{ bid.b_title }}")
        )
        url = reverse(self.view_name,
                      urlconf='gbe.urls')
        login_as(self.performer.performer_profile, self)
        data = {'theclass-teacher': self.performer.pk,
                'theclass-b_title': 'A class',
                'theclass-b_description': 'a description',
                'theclass-length_minutes': 60,
                'theclass-maximum_enrollment': 20,
                'theclass-fee': 0,
                'theclass-schedule_constraints': ['0'],
                'submit': 1,
                }
        response = self.client.post(url, data=data, follow=True)
        assert_right_mail_right_addresses(
            0,
            1,
            "bidder: %s, bid: %s" % (
                str(self.performer.performer_profile),
                data['theclass-b_title']),
            [privileged_profile.contact_email],
            from_email="class@notify.com")
