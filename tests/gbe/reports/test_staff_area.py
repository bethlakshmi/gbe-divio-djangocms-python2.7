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


class TestStaffArea(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()

    def test_staff_area_path(self):
        '''staff_area view should load
        '''
        show = ShowFactory()
        context = VolunteerContext(event=show)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['event', show.eventitem_id]))
        self.assertEqual(response.status_code, 200)

    def test_show_with_inactive(self):
        ''' view should load
        '''
        show = ShowFactory()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        context = VolunteerContext(event=show, profile=inactive)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['event', show.eventitem_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<tr style="color:red;">')

    def test_staff_area_path_fail(self):
        '''staff_area view should fail for non-authenticated users
        '''
        show = ShowFactory()
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['event', show.eventitem_id]))
        self.assertEqual(response.status_code, 403)

    def test_show_bad_event(self):
        show = ShowFactory()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['event', show.eventitem_id+100]))
        self.assertContains(response,
                            "Staff Schedules for None")

    def test_staff_area_bad_area(self):
        context = StaffAreaContext()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['area', context.area.pk+100]), follow=True)
        self.assertEqual(response.status_code, 404)

    def test_staff_area_with_inactive(self):
        '''staff_area view should load
        '''
        context = StaffAreaContext()
        inactive = ProfileFactory(
            display_name="DON'T SEE THIS",
            user_object__is_active=False
        )
        vol, opp = context.book_volunteer(volunteer=inactive)
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['area', context.area.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<tr style="color:red;">')

    def test_staff_area_default_display(self):
        '''staff_area view should load only the actually assigned volunteer
        '''
        context = StaffAreaContext()
        vol1, opp1 = context.book_volunteer()
        vol2, opp2 = context.book_volunteer(role="Pending Volunteer")
        vol3, opp3 = context.book_volunteer(role="Waitlisted")
        vol4, opp4 = context.book_volunteer(role="Rejected")
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['area', context.area.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(vol1))
        self.assertContains(response, role_commit_map["Volunteer"][1])
        self.assertNotContains(response, str(vol2))
        self.assertNotContains(response, str(vol3))
        self.assertNotContains(response, str(vol4))
        self.assertContains(response, "?filter=Potential")
        self.assertContains(response, reverse("edit_staff",
                                              urlconf='gbe.scheduling.urls',
                                              args=[context.area.pk]))

    def test_staff_area_potential_display_completed(self):
        '''staff_area view should load everything but rejected
            same code for event & staff area, so not retesting
        '''
        context = StaffAreaContext()
        context.conference.status = "completed"
        context.conference.save()
        vol1, opp1 = context.book_volunteer()
        vol2, opp2 = context.book_volunteer(role="Pending Volunteer")
        vol3, opp3 = context.book_volunteer(role="Waitlisted")
        vol4, opp4 = context.book_volunteer(role="Rejected")
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            "%s?filter=Potential" %
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['area', context.area.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(vol1))
        self.assertContains(response, str(vol2))
        self.assertContains(response, str(vol3))
        self.assertNotContains(response, str(vol4))
        self.assertContains(response, role_commit_map["Pending Volunteer"][1])
        self.assertContains(response, role_commit_map["Waitlisted"][1])
        self.assertContains(response, "?filter=Committed")
        self.assertNotContains(response, reverse("edit_staff",
                                                 urlconf='gbe.scheduling.urls',
                                                 args=[context.area.pk]))

    def test_show_completed(self):
        context = VolunteerContext()
        context.conference.status = "completed"
        context.conference.save()
        grant_privilege(self.profile, 'Act Reviewers')
        login_as(self.profile, self)
        response = self.client.get(
            reverse('staff_area',
                    urlconf="gbe.reporting.urls",
                    args=['event', context.event.eventitem_id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse(
            "edit_event",
            urlconf='gbe.scheduling.urls',
            args=[context.conference.conference_slug, context.sched_event.pk]))
