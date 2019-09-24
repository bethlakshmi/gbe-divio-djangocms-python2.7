from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from gbe.models import (
    Event,
    VolunteerInterest,
    VolunteerWindow,
)
from tests.factories.gbe_factories import(
    EventFactory,
    GenericEventFactory,
    VolunteerInterestFactory,
    VolunteerWindowFactory,
)
from django.contrib.admin.sites import AdminSite


class GBEChangeListTests(TestCase):
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
        response = self.client.get('/admin/gbe/volunteerinterest/')
        assert str(obj.volunteer.b_conference) in response.content

    def test_get_volunteer_window_conference(self):
        obj = VolunteerWindowFactory()
        response = self.client.get('/admin/gbe/volunteerwindow/')
        assert str(obj.day.conference) in response.content

    def test_get_event_subclass(self):
        obj = GenericEventFactory()
        response = self.client.get('/admin/gbe/event/')
        assert "GenericEvent" in response.content

    def test_get_event_no_subclass(self):
        obj = EventFactory()
        response = self.client.get('/admin/gbe/event/')
        assert "Event" in response.content
        assert str(obj) in response.content
