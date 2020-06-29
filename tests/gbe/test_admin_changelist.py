from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from gbe.models import (
    Event,
    VolunteerInterest,
)
from tests.factories.gbe_factories import(
    ActFactory,
    EventFactory,
    GenericEventFactory,
    TechInfoFactory,
    VolunteerInterestFactory,
)
from django.contrib.admin.sites import AdminSite


class GBEAdminChangeListTests(TestCase):
    def setUp(self):
        self.client = Client()
        password = 'mypassword'
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', password)
        self.client.login(
            username=self.privileged_user.username,
            password=password)

    def test_get_volunteer_interest_conference(self):
        obj = VolunteerInterestFactory()
        response = self.client.get('/admin/gbe/volunteerinterest/',
                                   follow=True)
        self.assertContains(response, obj.volunteer.b_conference)

    def test_get_event_subclass(self):
        obj = GenericEventFactory()
        response = self.client.get('/admin/gbe/event/', follow=True)
        self.assertContains(response, "GenericEvent")

    def test_get_event_no_subclass(self):
        obj = EventFactory()
        response = self.client.get('/admin/gbe/event/', follow=True)
        self.assertContains(response, "Event")
        self.assertContains(response, str(obj))

    def test_get_techinfo(self):
        act = ActFactory()
        response = self.client.get('/admin/gbe/techinfo/', follow=True)
        self.assertContains(response, "Techinfo: %s" % act.b_title)

    def test_get_techinfo_no_act(self):
        tech = TechInfoFactory()
        response = self.client.get('/admin/gbe/techinfo/', follow=True)
        self.assertContains(response, "Techinfo: (deleted act)")
