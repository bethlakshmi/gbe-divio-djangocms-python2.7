from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from tests.factories.gbe_factories import(
    ClassFactory,
    ProfileFactory,
)
from tests.factories.scheduler_factories import(
    EventItemFactory,
    LocationFactory,
    ResourceAllocationFactory,
    ResourceFactory,
)
from tests.contexts import(
    ActTechInfoContext,
    ClassContext,
    ShowContext,
    VolunteerContext,
)
from django.contrib.admin.sites import AdminSite
from datetime import datetime


class SchedulerChangeListTests(TestCase):
    def setUp(self):
        self.client = Client()
        password = 'mypassword'
        self.privileged_user = User.objects.create_superuser(
            'myuser', 'myemail@test.com', password)
        self.client.login(
            username=self.privileged_user.username,
            password=password)

    def test_get_ordering_performer(self):
        context = ActTechInfoContext(act_role="Featured")
        response = self.client.get('/admin/scheduler/ordering/',
                                   follow=True)
        self.assertContains(response, str(context.performer))
        self.assertContains(response, "Featured")

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

    def test_get_allocation_eventitem_no_resource(self):
        allocation = ResourceAllocationFactory(
            resource=ResourceFactory())
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response,
                            "Error in resource allocation, no resource")
        self.assertContains(response, "Resource (no child)")

    def test_get_allocation_eventitem_no_child_workeritem_no_child(self):
        allocation = ResourceAllocationFactory(
            event__eventitem=EventItemFactory())
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "no child")
        self.assertContains(response, "Worker Item (no child_event)")

    def test_get_allocation_resource_type(self):
        context = VolunteerContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, str("Profile"))
        self.assertContains(response, "Volunteer")
        self.assertContains(response, str(context.conference))

    def test_get_allocation_class_type(self):
        context = ClassContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "Class")
        self.assertContains(response, "location")

    def test_get_allocation_show_type(self):
        context = ShowContext()
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "Act")
        self.assertContains(response, "Show")

    def test_get_allocation_no_locationresource_child(self):
        allocation = ResourceAllocationFactory(resource=LocationFactory())
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "No Location Item")

    def test_get_eventcontainer(self):
        context = ShowContext()
        rehearsal, slot = context.make_rehearsal()
        response = self.client.get('/admin/scheduler/eventcontainer/',
                                   follow=True)
        self.assertContains(response, rehearsal.e_title)
        self.assertContains(response, context.show.e_title)
        self.assertContains(response, context.conference.conference_name)
