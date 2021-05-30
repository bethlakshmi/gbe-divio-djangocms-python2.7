from django.urls import reverse
from django.test import TestCase, Client
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.gbe_factories import (
    ProfileFactory,
    ShowFactory,
)
from tests.contexts import (
    StaffAreaContext,
    VolunteerContext,
)
from gbetext import role_commit_map


class TestAllVolunteer(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        self.url = reverse('all_volunteers', urlconf="gbe.reporting.urls")

    def test_review_not_visible_without_permission(self):
        show = ShowFactory()
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_show_volunteer(self):
        '''staff_area view should load
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        grant_privilege(self.profile, 'Act Coordinator')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, show.e_title)
        self.assertContains(response, context.opportunity.e_title)
        self.assertContains(response, reverse(
            'mail_to_individual',
            urlconf='gbe.email.urls',
            args=[context.profile.resourceitem_id]))
        self.assertContains(response, reverse(
            'edit_event',
            urlconf='gbe.scheduling.urls',
            args=[context.conference.conference_slug, context.opp_event.pk]))

    def test_show_with_inactive(self):
        ''' view should load
        '''
        show = ShowFactory()
        inactive = ProfileFactory(
            display_name="Inactive User",
            user_object__is_active=False
        )
        context = VolunteerContext(event=show, profile=inactive)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, show.e_title)
        self.assertContains(response, context.opportunity.e_title)
        self.assertContains(
            response,
            '<div class="gbe-form-error">')
        self.assertContains(response, inactive.display_name)

    def test_show_approval_needed_event(self):
        show = ShowFactory()
        context = VolunteerContext(event=show)
        context.opp_event.approval_needed = True
        context.opp_event.save()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertContains(response, context.opportunity.e_title)
        self.assertContains(response, 'class="approval_needed"')

    def test_staff_area_role_display(self):
        '''staff_area view should load only the actually assigned volunteer
        '''
        context = StaffAreaContext()
        vol1, opp1 = context.book_volunteer()
        vol2, opp2 = context.book_volunteer(role="Pending Volunteer")
        vol3, opp3 = context.book_volunteer(role="Waitlisted")
        vol4, opp4 = context.book_volunteer(role="Rejected")
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(vol1))
        self.assertContains(response, str(vol2))
        self.assertContains(response, str(vol3))
        self.assertNotContains(response, str(vol4))
        self.assertContains(response, reverse("review_pending",
                                              urlconf='gbe.scheduling.urls'))
        self.assertContains(response, context.area.title)

    def test_staff_area_conference_completed(self):
        '''staff_area view should load everything but rejected
            same code for event & staff area, so not retesting
        '''
        context = StaffAreaContext()
        context.conference.status = "completed"
        context.conference.save()
        vol1, opp1 = context.book_volunteer()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get("%s?conf_slug=%s" % (
            self.url,
            context.conference.conference_slug))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(vol1))
        self.assertNotContains(response, reverse(
            'edit_event',
            urlconf='gbe.scheduling.urls',
            args=[context.conference.conference_slug, opp1.event.pk]))
