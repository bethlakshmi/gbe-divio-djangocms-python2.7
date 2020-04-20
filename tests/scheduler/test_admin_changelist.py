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

    def test_get_allocation_resource_type(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, str("Profile"))

    def test_get_allocation_genericevent_type(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "Volunteer")

    def test_get_allocation_class_type(self):
        context = ClassContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "Class")

    def test_get_eventitem_genericevent(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/eventitem/',
                                   follow=True)
        self.assertContains(response, "Volunteer")
        self.assertContains(response, str(context.conference))

    def test_get_eventitem_class_type(self):
        context = ClassContext()
        response = self.client.get('/admin/scheduler/eventitem/',
                                   follow=True)
        self.assertContains(response, "Class")

    def test_get_eventcontainer_conference(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/eventcontainer/',
                                   follow=True)
        self.assertContains(response, str(context.conference))
