from django.test import (
    Client,
    TestCase
)
from django.contrib.auth.models import User
from tests.factories.gbe_factories import(
    ClassFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    login_as,
    setup_admin_w_privs,
)
from tests.factories.scheduler_factories import(
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

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = setup_admin_w_privs([])

    def setUp(self):
        self.client = Client()
        login_as(self.privileged_user, self)

    def test_get_ordering_performer(self):
        context = ActTechInfoContext(act_role="Featured")
        response = self.client.get('/admin/scheduler/ordering/',
                                   follow=True)
        self.assertContains(
            response,
            "class: Bio, id: %d" % context.performer.pk)
        self.assertContains(
            response,
            context.performer.contact.display_name)
        self.assertContains(response, "Featured")

    def test_get_allocation_no_resource(self):
        allocation = ResourceAllocationFactory(
            resource=ResourceFactory())
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response,
                            "Error in resource allocation, no resource")
        self.assertContains(response, "Resource (no child)")

    def test_get_allocation_resource_type(self):
        context = VolunteerContext()
        response = self.client.get(
            '/admin/scheduler/peopleallocation/?event__eventlabel__text=%s' % (
                context.conference.conference_slug), follow=True)
        self.assertContains(response, "Volunteer")
        self.assertContains(response, str(context.conference.conference_slug))
        self.assertContains(response, context.people.pk)
        self.assertContains(response, context.profile.display_name)

    def test_get_allocation_class_type(self):
        context = ClassContext()
        response = self.client.get(
            '/admin/scheduler/peopleallocation/?event__eventlabel__text=%s' % (
                context.conference.conference_slug), follow=True)
        self.assertContains(response, "Class")
        self.assertContains(response, context.people.pk)
        self.assertContains(response, context.teacher.contact.display_name)

    def test_get_allocation_show_type(self):
        context = ShowContext()
        response = self.client.get(
            '/admin/scheduler/peopleallocation/?event__eventlabel__text=%s' % (
                context.conference.conference_slug), follow=True)
        self.assertContains(response, "Show")
        self.assertContains(response, context.people.pk)
        self.assertContains(response, context.performer.contact.display_name)

    def test_get_people(self):
        context = ShowContext()
        response = self.client.get('/admin/scheduler/people/',
                                   follow=True)
        self.assertContains(response, context.people.pk)
        self.assertContains(response, context.performer.pk)
        self.assertContains(response, context.performer.__class__.__name__)
        self.assertContains(response, context.performer.contact.display_name)

    def test_get_allocation_no_locationresource_child(self):
        allocation = ResourceAllocationFactory(resource=LocationFactory())
        response = self.client.get('/admin/scheduler/resourceallocation/',
                                   follow=True)
        self.assertContains(response, "No Location Item")
