from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from scheduler.models import (
    ResourceAllocation,
)
from tests.factories.gbe_factories import(
    ClassFactory,
    ProfileFactory,
)
from tests.contexts import(
    ClassContext,
    VolunteerContext,
)
from django.contrib.admin.sites import AdminSite


class SchedulerChangeListTests(TestCase):
    def setUp(self):
        self.client = Client()
        password = 'mypassword'
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', password)
        self.client.login(
            username=self.privileged_user.username,
            password=password)

    def test_get_resource_email(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/')
        assert str(context.worker._item.contact_email) in response.content

    def test_get_allocation_resource_type(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/')
        assert str("Profile") in response.content

    def test_get_allocation_genericevent_type(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/')
        assert "Volunteer" in response.content

    def test_get_allocation_class_type(self):
        context = ClassContext()
        response = self.client.get('/admin/scheduler/resourceallocation/')
        assert "Class" in response.content

    def test_get_eventitem_genericevent(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/eventitem/')
        assert "Volunteer" in response.content
        assert str(context.conference) in response.content

    def test_get_eventitem_class_type(self):
        context = ClassContext()
        response = self.client.get('/admin/scheduler/eventitem/')
        assert "Class" in response.content

    def test_get_eventcontainer_conference(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/eventcontainer/')
        assert str(context.conference) in response.content
