from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    ConferenceDayFactory,
    ProfileFactory,
)
from gbe.models import (
    Conference,
    StaffArea,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from tests.factories.scheduler_factories import (
    SchedEventFactory,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
    VolunteerContext,
)
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
)
from datetime import (
    timedelta,
)
from gbe_forms_text import event_styles_complete


class TestManageEventList(TestCase):
    view_name = 'manage_event_list'
    conf_tab = '<a class="dropdown-item" href="%s?">%s</a>'
    active_conf = (
        '<a class="btn btn-light dropdown-toggle" href="#" role="button" ' +
        'id="dropdownMenuLink" data-toggle="dropdown" aria-haspopup="true" ' +
        'aria-expanded="false">%s</a>')

    def setUp(self):
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.user = ProfileFactory.create().user_object
        cls.privileged_profile = ProfileFactory()
        cls.privileged_user = cls.privileged_profile.user_object
        grant_privilege(cls.privileged_user, 'Scheduling Mavens')
        cls.url = reverse(cls.view_name, urlconf="gbe.scheduling.urls")
        cls.volunteer_context = VolunteerContext()
        cls.day = cls.volunteer_context.conf_day
        cls.class_context = ClassContext(conference=cls.day.conference)
        cls.show_context = ShowContext(conference=cls.day.conference)
        cls.staff_context = StaffAreaContext(conference=cls.day.conference)
        booking, cls.vol_opp = cls.staff_context.book_volunteer()

    def assert_visible_input_selected(
            self,
            response,
            conf_slug,
            input_field,
            input_index,
            value,
            checked=True):
        if checked:
            checked = 'checked '
        else:
            checked = ''
        template_input = '<input type="checkbox" name="%s-%s" value="%s" ' + \
                         'class="form-check-input" id="id_%s-%s_%d" %s/>'
        assert_string = template_input % (
            conf_slug,
            input_field,
            value,
            conf_slug,
            input_field,
            input_index,
            checked)
        self.assertContains(response, assert_string, html=True)

    def assert_hidden_input_selected(
            self,
            response,
            conf_slug,
            input_field,
            input_index,
            value,
            exists=True):
        template_input = '<input type="hidden" name="%s-%s" value="%d"' + \
            ' id="id_%s-%s_%d" />'

        assert_string = template_input % (
            conf_slug,
            input_field,
            value,
            conf_slug,
            input_field,
            input_index)
        if exists:
            self.assertContains(response, assert_string, html=True)
        else:
            self.assertNotContains(response, assert_string, html=True)

    def test_no_login_gives_error(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_bad_user(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_good_user_get_success(self):
        old_conf_day = ConferenceDayFactory(
            conference__status="completed",
            day=self.day.day + timedelta(3))
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.active_conf % self.day.conference.conference_slug,
            html=True)
        self.assertContains(
            response,
            self.conf_tab % (
                reverse(self.view_name,
                        urlconf="gbe.scheduling.urls",
                        args=[old_conf_day.conference.conference_slug]),
                old_conf_day.conference.conference_slug),
            html=True)
        self.assertContains(
            response,
            self.day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(
            response,
            old_conf_day.day.strftime(GBE_DATE_FORMAT))

    def test_good_user_get_staff_area(self):
        other_staff_context = StaffAreaContext()
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.staff_context.area.title)
        self.assertNotContains(
            response,
            other_staff_context.area.title)

    def test_good_user_get_create_edit(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-calendar_type" % self.day.conference.conference_slug: [
                0, 1, 2],
            "filter": "Filter",
        }
        response = self.client.get(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<i class="fa fa-pencil" aria-hidden="true">')

    def test_good_user_get_success_pick_conf(self):
        old_conf_day = ConferenceDayFactory(
            conference__status="completed",
            day=self.day.day + timedelta(3))
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[old_conf_day.conference.conference_slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.active_conf % old_conf_day.conference.conference_slug,
            html=True)
        self.assertContains(
            response,
            self.conf_tab % (
                reverse(self.view_name,
                        urlconf="gbe.scheduling.urls",
                        args=[self.day.conference.conference_slug]),
                self.day.conference.conference_slug),
            html=True)
        self.assertContains(
            response,
            old_conf_day.day.strftime(GBE_DATE_FORMAT))
        self.assertNotContains(
            response,
            self.day.day.strftime(GBE_DATE_FORMAT))

    def test_good_user_get_no_create_edit(self):
        old_conf_day = ConferenceDayFactory(
            conference__status="completed",
            day=self.day.day + timedelta(3))
        context = ClassContext(conference=old_conf_day.conference)
        vol_context = VolunteerContext(conference=old_conf_day.conference)
        staff_context = StaffAreaContext(conference=old_conf_day.conference)
        booking, self.vol_opp = staff_context.book_volunteer()
        data = {
            "%s-calendar_type" % old_conf_day.conference.conference_slug: [
                0, 1, 2],
            "filter": "Filter",
        }
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.scheduling.urls",
                      args=[old_conf_day.conference.conference_slug])
        response = self.client.get(url, data)
        self.assertContains(
            response,
            '<i class="fa fa-trash-o" aria-hidden="true">')
        self.assertNotContains(
            response,
            '<i class="fa fa-pencil" aria-hidden="true">')
        self.assertNotContains(
            response,
            '<i class="fa fa-plus" aria-hidden="true">')
        self.assertContains(response, vol_context.opp_event.title)
        self.assertContains(response, reverse(
            'detail_view',
            urlconf='gbe.scheduling.urls',
            args=[vol_context.sched_event.pk]))
        self.assertContains(response, vol_context.sched_event.title)
        self.assertNotContains(response, reverse(
            "edit_staff",
            urlconf="gbe.scheduling.urls",
            args=[staff_context.area.pk]))

    def test_good_user_get_conference_cal(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-calendar_type" % self.day.conference.conference_slug: 1,
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.class_context.bid.b_title)
        self.assert_visible_input_selected(
            response,
            self.day.conference.conference_slug,
            "calendar_type",
            1,
            1)
        self.assert_visible_input_selected(
            response,
            self.day.conference.conference_slug,
            "calendar_type",
            0,
            0,
            checked=False)
        # conference class bids do not yet have copy feature.
        self.assertNotContains(
            response,
            'href="%s" data-toggle="tooltip" title="Copy"' % (
                reverse("copy_event_schedule",
                        urlconf="gbe.scheduling.urls",
                        args=[self.class_context.sched_event.pk])))

    def test_good_user_get_conference_bad_filter(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-calendar_type" % self.day.conference.conference_slug: "bad",
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Select a valid choice. bad is not one of the available choices.")

    def test_good_user_get_all_cals(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-calendar_type" % self.day.conference.conference_slug: [
                0, 1, 2],
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.class_context.bid.b_title)
        self.assertContains(response, self.show_context.sched_event.title)
        self.assertContains(response, self.vol_opp.event.title)
        self.assertContains(response, '<td>Volunteer</td>')
        self.assertContains(response,
                            self.volunteer_context.opp_event.title)
        self.assertContains(
            response,
            ('<a href="%s" class="gbe-table-link" data-toggle="tooltip" ' +
             'title="Edit">%s</a>') % (
                reverse('edit_event',
                        urlconf='gbe.scheduling.urls',
                        args=[self.day.conference.conference_slug,
                              self.volunteer_context.sched_event.pk]),
                self.volunteer_context.sched_event.title),
            html=True)
        for value in range(0, 2):
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "calendar_type",
                1,
                1)

    def test_good_user_get_day(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-day" % self.day.conference.conference_slug: self.day.pk,
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.show_context.sched_event.title)
        self.assertContains(response, self.class_context.bid.b_title)
        counter = 0
        for day in self.day.conference.conferenceday_set.all().order_by('day'):
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "day",
                counter,
                day.pk,
                checked=(day == self.day))
            counter += 1
        for value in range(0, 2):
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "calendar_type",
                1,
                1,
                checked=False)

    def test_good_user_get_empty_day(self):
        new_day = ConferenceDayFactory(conference=self.day.conference,
                                       day=self.day.day+timedelta(14))
        login_as(self.privileged_profile, self)
        data = {
            "%s-day" % self.day.conference.conference_slug: new_day.pk,
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.show_context.sched_event.title)
        self.assertNotContains(response, self.class_context.bid.b_title)
        counter = 0
        for day in self.day.conference.conferenceday_set.all().order_by('day'):
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "day",
                counter,
                day.pk,
                checked=(day == new_day))
            counter += 1

    def test_good_user_filter_staff_area(self):
        other_staff_area = StaffAreaContext(
            conference=self.day.conference
        )
        login_as(self.privileged_profile, self)
        data = {
            "%s-staff_area" % self.day.conference.conference_slug: (
                self.staff_context.area.pk),
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.vol_opp.event.title)
        self.assertContains(
            response,
            ('<a href="%s" class="gbe-table-link" data-toggle="tooltip" ' +
             'title="Edit">%s</a>') % (
                reverse("edit_staff",
                        urlconf="gbe.scheduling.urls",
                        args=[self.staff_context.area.pk]),
                self.staff_context.area.slug),
            html=True)
        index = 0
        for area in StaffArea.objects.filter(
                conference=self.day.conference).order_by('title'):
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "staff_area",
                index,
                area.pk,
                checked=(area == self.staff_context.area))
            index += 1

    def test_good_user_filter_event_style(self):
        login_as(self.privileged_profile, self)
        data = {
            "%s-event_style" % self.day.conference.conference_slug: (
                'Volunteer'),
            "filter": "Filter",
        }
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.vol_opp.event.title)
        self.assertNotContains(response, self.show_context.sched_event.title)
        self.assertNotContains(response, self.class_context.sched_event.title)
        index = 0
        for event_style, description in event_styles_complete:
            self.assert_visible_input_selected(
                response,
                self.day.conference.conference_slug,
                "event_style",
                index,
                event_style,
                checked=(event_style == "Volunteer"))
            index += 1
