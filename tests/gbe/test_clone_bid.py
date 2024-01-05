from django.urls import reverse
from django.test import TestCase
from django.test import Client

from tests.factories.gbe_factories import (
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    ProfileFactory,
    UserMessageFactory,
    VendorFactory,
)
from gbe.models import (
    Act,
    Class,
    UserMessage,
    Vendor,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    clear_conferences,
    login_as,
)
from gbetext import default_clone_msg


class TestCloneBid(TestCase):
    view_name = 'clone_bid'

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        UserMessage.objects.all().delete()
        clear_conferences()
        cls.old_conference = ConferenceFactory(
            status="completed",
            accepting_bids=False)
        cls.current_conference = ConferenceFactory(
            status="upcoming",
            accepting_bids=True)

    def clone_act(self):
        bid = ActFactory(b_conference=self.old_conference)
        Act.objects.filter(b_title=bid.b_title,
                           b_conference=self.current_conference).delete()

        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Act',
                              'bid_id': bid.id})
        login_as(bid.performer.contact, self)

        response = self.client.get(url, follow=True)
        return response, bid

    def clone_vendor(self):
        bid = VendorFactory(b_conference=self.old_conference)
        profile = bid.business.owners.all().first()
        Vendor.objects.filter(business=bid.business,
                              b_conference=self.current_conference).delete()

        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Vendor',
                              'bid_id': bid.id})
        login_as(profile, self)

        response = self.client.get(url)
        return response, bid

    def clone_class(self):
        bid = ClassFactory(b_conference=self.old_conference,
                           difficulty="Hard")
        bid.b_title = "Factory is broken"
        bid.save()
        count = Class.objects.filter(
            b_title=bid.b_title,
            b_conference=self.current_conference).count()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Class',
                              'bid_id': bid.id})
        login_as(bid.teacher.contact, self)

        response = self.client.get(url, follow=True)
        return response, count, bid

    def test_clone_act_succeed(self):
        response, bid = self.clone_act()
        self.assertTrue(Act.objects.filter(
            b_title=bid.b_title,
            b_conference=self.current_conference).exists())

    def test_clone_vendor_succeed(self):
        response, bid = self.clone_vendor()
        self.assertTrue(Vendor.objects.filter(
            business__name=bid.business.name,
            b_conference=self.current_conference).exists())

    # following test fails, not sure why.
    # ClassFactory creates an instance of gbe.Class w/o data,
    # which doesn't seem to persist to the db

    def test_clone_class_succeed(self):
        response, count, bid = self.clone_class()
        self.assertEqual(
            1 + count,
            Class.objects.filter(b_title=bid.b_title,
                                 b_conference=self.current_conference).count())
        self.assertEqual(Class.objects.all().latest('pk').difficulty, "Hard")

    def test_clone_bid_bad_bid_type(self):
        bid = ActFactory(b_conference=self.old_conference)
        Act.objects.filter(b_title=bid.b_title,
                           b_conference=self.current_conference).delete()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Steakknife',
                              'bid_id': bid.id})
        login_as(bid.performer.contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_clone_bid_wrong_user(self):
        # apparently cleaning is not needed, causes problem in Djang 1.11
        # Conference.objects.all().delete()
        bid = ActFactory(b_conference=self.old_conference)
        Act.objects.filter(b_title=bid.b_title,
                           b_conference=self.current_conference).delete()
        url = reverse(self.view_name,
                      urlconf="gbe.urls",
                      kwargs={'bid_type': 'Act',
                              'bid_id': bid.id})
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_clone_act_make_message(self):
        response, bid = self.clone_act()
        assert_alert_exists(
            response, 'success', 'Success', default_clone_msg)

    def test_clone_class_make_message(self):
        response, count, bid = self.clone_class()
        assert_alert_exists(
            response, 'success', 'Success', default_clone_msg)

    def test_clone_act_has_message(self):
        msg = UserMessageFactory(
            view='CloneBidView',
            code='CLONE_ACT_SUCCESS')
        response, bid = self.clone_act()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)

    def test_clone_class_has_message(self):
        msg = UserMessageFactory(
            view='CloneBidView',
            code='CLONE_CLASS_SUCCESS')
        response, count, bid = self.clone_class()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
