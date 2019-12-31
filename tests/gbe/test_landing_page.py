import nose.tools as nt
from django.test import TestCase
from datetime import datetime
import pytz
from django.test import Client
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import(
    ActFactory,
    ClassFactory,
    ConferenceFactory,
    CostumeFactory,
    FlexibleEvaluationFactory,
    GenericEventFactory,
    PersonaFactory,
    ProfileFactory,
    TroupeFactory,
    UserFactory,
    VendorFactory,
    VolunteerFactory,
)
from tests.factories.scheduler_factories import (
    LabelFactory,
    SchedEventFactory,
    ResourceAllocationFactory,
    WorkerFactory,
)
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    set_image,
    make_vendor_app_purchase,
    make_vendor_app_ticket,
    make_act_app_ticket,
    make_act_app_purchase,
)
from tests.contexts import ActTechInfoContext
from django.utils.formats import date_format
from gbetext import interested_explain_msg
from datetime import (
    datetime,
    timedelta,
)


class TestIndex(TestCase):
    '''Tests for index view'''
    view_name = 'home'

    def setUp(self):
        self.client = Client()
        # Conference Setup
        self.factory = RequestFactory()
        self.current_conf = ConferenceFactory(accepting_bids=True,
                                              status='upcoming')
        self.previous_conf = ConferenceFactory(accepting_bids=False,
                                               status='completed')

        # User/Human setup
        self.profile = ProfileFactory()
        self.performer = PersonaFactory(performer_profile=self.profile,
                                        contact=self.profile)
        # Bid types previous and current
        self.current_act = ActFactory(performer=self.performer,
                                      submitted=True,
                                      b_conference=self.current_conf)
        self.previous_act = ActFactory(performer=self.performer,
                                       submitted=True,
                                       b_conference=self.previous_conf)
        self.current_class = ClassFactory(teacher=self.performer,
                                          submitted=True,
                                          accepted=3,
                                          b_conference=self.current_conf,
                                          e_conference=self.current_conf)
        self.previous_class = ClassFactory(teacher=self.performer,
                                           submitted=True,
                                           accepted=3,
                                           b_conference=self.previous_conf,
                                           e_conference=self.previous_conf)

        self.current_vendor = VendorFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_vendor = VendorFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)

        self.current_costume = CostumeFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_costume = CostumeFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)
        self.current_volunteer = VolunteerFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.current_conf)
        self.previous_volunteer = VolunteerFactory(
            profile=self.profile,
            submitted=True,
            b_conference=self.previous_conf)

        # Event assignments, previous and current
        current_opportunity = GenericEventFactory(
            e_conference=self.current_conf,
            type='Volunteer')
        previous_opportunity = GenericEventFactory(
            e_conference=self.previous_conf)

        self.current_sched = SchedEventFactory(
            eventitem=current_opportunity,
            starttime=datetime(2016, 2, 5, 12, 30, 0, 0),
            max_volunteer=10)
        self.previous_sched = SchedEventFactory(
            eventitem=previous_opportunity,
            starttime=datetime(2015, 2, 25, 12, 30, 0, 0),
            max_volunteer=10)

        self.current_class_sched = SchedEventFactory(
            eventitem=self.current_class,
            starttime=datetime(2016, 2, 5, 2, 30, 0, 0),
            max_volunteer=10)
        self.previous_class_sched = SchedEventFactory(
            eventitem=self.previous_class,
            starttime=datetime(2015, 2, 25, 2, 30, 0, 0),
            max_volunteer=10)

        worker = WorkerFactory(_item=self.profile, role='Volunteer')
        for schedule_item in [self.current_sched,
                              self.previous_sched]:
            volunteer_assignment = ResourceAllocationFactory(
                event=schedule_item,
                resource=worker
            )
            LabelFactory(text="label %d" % volunteer_assignment.pk,
                         allocation=volunteer_assignment)

        persona_worker = WorkerFactory(_item=self.performer,
                                       role='Teacher')
        for schedule_item in [self.current_class_sched,
                              self.previous_class_sched]:
            volunteer_assignment = ResourceAllocationFactory(
                event=schedule_item,
                resource=worker
            )

    def assert_event_is_present(self, response, event):
        ''' test all parts of the event being on the landing page schedule'''
        self.assertContains(response, event.eventitem.e_title)
        self.assertContains(response,
                            date_format(event.start_time, "DATETIME_FORMAT"))
        self.assertContains(response, reverse(
            'detail_view',
            urlconf="gbe.scheduling.urls",
            args=[event.eventitem.eventitem_id]))

    def assert_event_is_not_present(self, response, event):
        ''' test all parts of the event being on the landing page schedule'''
        self.assertNotContains(response, event.eventitem.e_title)
        self.assertNotContains(
            response,
            date_format(event.start_time, "DATETIME_FORMAT"))
        self.assertNotContains(response, reverse(
            'detail_view',
            urlconf="gbe.scheduling.urls",
            args=[event.eventitem.eventitem_id]))

    def get_landing_page(self):
        self.url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        return self.client.get(self.url)

    def test_no_profile(self):
        url = reverse('home', urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url)
        nt.assert_true("Your Expo" in response.content)

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        response = self.get_landing_page()
        self.assertEqual(response.status_code, 200)
        content = response.content
        does_not_show_previous = (
            self.previous_act.b_title not in content and
            self.previous_class.b_title not in content and
            self.previous_vendor.b_title not in content and
            self.previous_costume.b_title not in content and
            reverse('volunteer_view',
                    urlconf='gbe.urls',
                    args=[self.previous_volunteer.id]) not in content)
        shows_all_current = (
            self.current_act.b_title in content and
            self.current_class.b_title in content and
            self.current_vendor.b_title in content and
            self.current_costume.b_title in content and
            reverse('volunteer_edit',
                    urlconf='gbe.urls',
                    args=[self.current_volunteer.id]) in content)
        assert does_not_show_previous
        assert shows_all_current
        self.assert_event_is_present(response, self.current_sched)
        self.assert_event_is_not_present(response, self.previous_sched)
        self.assert_event_is_present(response, self.current_class_sched)
        self.assert_event_is_not_present(response, self.previous_class_sched)
        self.assertNotContains(response, "shadow-red")

    def test_historical_view(self):
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(
            url,
            data={'historical': 1})
        content = response.content
        self.assertEqual(response.status_code, 200)
        shows_all_previous = (
            self.previous_act.b_title in content and
            self.previous_class.b_title in content and
            self.previous_vendor.b_title in content and
            self.previous_costume.b_title in content in content)
        does_not_show_current = (
            self.current_act.b_title not in content and
            self.current_class.b_title not in content and
            self.current_vendor.b_title not in content and
            self.current_costume.b_title not in content)
        nt.assert_true(shows_all_previous and
                       does_not_show_current)
        self.assert_event_is_present(response, self.previous_sched)
        self.assert_event_is_not_present(response, self.current_sched)
        self.assert_event_is_present(response, self.previous_class_sched)
        self.assert_event_is_not_present(response, self.current_class_sched)

    def test_as_privileged_user(self):
        staff_profile = ProfileFactory()
        grant_privilege(staff_profile, "Ticketing - Admin")
        login_as(staff_profile, self)
        url = reverse('admin_landing_page', urlconf='gbe.urls',
                      args=[staff_profile.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        nt.assert_true("You are viewing a" in response.content)

    def test_acts_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Act Reviewers")
        login_as(staff_profile, self)
        act = ActFactory(submitted=True,
                         b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(act.b_title in response.content)

    def test_act_was_reviewed(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Act Reviewers")
        login_as(staff_profile, self)
        reviewed_act = ActFactory(submitted=True,
                                  b_conference=self.current_conf)
        FlexibleEvaluationFactory(bid=reviewed_act,
                                  evaluator=staff_profile)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertNotContains(response, reviewed_act.b_title)

    def test_classes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Class Reviewers")
        login_as(staff_profile, self)
        klass = ClassFactory(submitted=True,
                             b_conference=self.current_conf,
                             e_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(klass.b_title in response.content)

    def test_volunteers_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Volunteer Reviewers")
        login_as(staff_profile, self)
        volunteer = VolunteerFactory(submitted=True,
                                     b_conference=self.current_conf)

        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        nt.assert_true(volunteer.b_title in response.content)

    def test_vendors_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Vendor Reviewers")
        login_as(staff_profile, self)
        vendor = VendorFactory(submitted=True,
                               b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)

        nt.assert_true(vendor.b_title in response.content)

    def test_costumes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Costume Reviewers")
        login_as(staff_profile, self)
        costume = CostumeFactory(submitted=True,
                                 b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)

        assert costume.b_title in response.content

    def test_profile_image(self):
        set_image(self.performer)
        response = self.get_landing_page()
        self.assertContains(response, self.performer.name)
        self.assertContains(response, self.performer.img.url)

    def test_cannot_edit_troupe_if_not_contact(self):
        troupe = TroupeFactory()
        member = PersonaFactory()
        troupe.membership.add(member)
        url = reverse("home", urlconf="gbe.urls")
        login_as(member.performer_profile, self)
        response = self.client.get(url)
        assert response.content.count("(Click to edit)") == 1

    def test_review_act_w_troupe(self):
        # causes a check on act complete state that is different from soloist
        troupe = TroupeFactory()
        member = PersonaFactory()
        troupe.membership.add(member)
        act = ActFactory(performer=troupe,
                         submitted=True,
                         b_conference=self.current_conf)
        login_as(member.performer_profile, self)
        url = reverse("home", urlconf="gbe.urls")
        response = self.client.get(url)
        print "Act::: " + act.b_title
        print response.content
        assert act.b_title in response.content

    def test_two_acts_one_show(self):
        '''Basic test of landing_page view
        '''
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        # Bid types previous and current
        current_act_context = ActTechInfoContext(
            performer=self.performer,
            act=self.current_act,
            conference=self.current_conf)
        second_act_context = ActTechInfoContext(
            performer=self.performer,
            conference=self.current_conf,
            show=current_act_context.show)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            second_act_context.act.b_title,
                            count=3)
        self.assertContains(response,
                            second_act_context.show.e_title,
                            count=2)

    def test_interest(self):
        '''Basic test of landing_page view
        '''
        context = ClassContext(
            conference=self.current_conf)
        context.set_interest(self.profile)
        response = self.get_landing_page()
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            self.url))

    def test_teacher_interest(self):
        '''Basic test of landing_page view
        '''
        context = ClassContext(
            conference=self.current_conf,
            teacher=PersonaFactory(performer_profile=self.profile))
        interested = []
        for i in range(0, 3):
            interested += [context.set_interest()]
        response = self.get_landing_page()
        for person in interested:
            self.assertContains(
                response,
                "%s &lt;%s&gt;;" % (person.display_name,
                                    person.user_object.email))
        self.assertContains(response,
                            interested_explain_msg)

    def test_historical_no_interest(self):
        context = ClassContext(
            conference=self.previous_conf,
            teacher=PersonaFactory(performer_profile=self.profile))
        interested = []
        for i in range(0, 3):
            interested += [context.set_interest()]
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(
            url,
            data={'historical': 1})
        content = response.content
        for person in interested:
            self.assertNotContains(
                response,
                "%s &lt;%s&gt;;</br>" % (person.display_name,
                                         person.user_object.email))
        self.assertNotContains(response,
                               interested_explain_msg)

    def test_eval_ready(self):
        '''Basic test of landing_page view
        '''
        context = ClassContext(
            conference=self.current_conf,
            starttime=datetime.now()-timedelta(days=1))
        context.set_interest(self.profile)
        context.setup_eval()
        response = self.get_landing_page()
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            eval_link,
            self.url))

    def test_eval_answered(self):
        '''Basic test of landing_page view
        '''
        context = ClassContext(
            conference=self.current_conf,
            starttime=datetime.now()-timedelta(days=1))
        context.set_interest(self.profile)
        context.set_eval_answerer(self.profile)
        response = self.get_landing_page()
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            eval_link,
            self.url))
        self.assertContains(response, "You have already rated this class")

    def test_unpaid_act_draft(self):
        self.unpaid_act = ActFactory(performer=self.performer,
                                     submitted=False,
                                     b_conference=self.current_conf)
        expected_string = (
            '<span class="shadow-red"><b>%s</b></span> - Not submitted'
            ) % self.unpaid_act.b_title
        bpt_event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)
        self.assertContains(response, "%d/%s" % (self.profile.user_object.id,
                                                 bpt_event_id))

    def test_paid_act_draft(self):
        make_act_app_purchase(self.current_conf,
                              self.profile.user_object)
        make_act_app_purchase(self.current_conf,
                              self.profile.user_object)
        self.paid_act = ActFactory(performer=self.performer,
                                     submitted=False,
                                     b_conference=self.current_conf)
        expected_string = (
            '<span class="shadow-red"><b>%s</b></span> - Not submitted'
            ) % self.paid_act.b_title
        bpt_event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)
        self.assertNotContains(response, "%d/%s" % (
            self.profile.user_object.id,
            bpt_event_id))
        self.assertContains(response, "Fee has been paid, submit NOW!")

    def test_unpaid_vendor_draft(self):
        self.unpaid_vendor = VendorFactory(
            profile=self.profile,
            submitted=False,
            b_conference=self.current_conf)
        expected_string = (
            '<span class="shadow-red"><b>%s</b></span>'
            ) % self.unpaid_vendor.b_title
        bpt_event_id = make_vendor_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)
        self.assertContains(response, "%d/%s" % (self.profile.user_object.id,
                                                 bpt_event_id))

    def test_paid_vendor_draft(self):
        make_vendor_app_purchase(self.current_conf,
                                 self.profile.user_object)
        make_vendor_app_purchase(self.current_conf,
                                 self.profile.user_object)
        self.paid_vendor = VendorFactory(
            profile=self.profile,
            submitted=False,
            b_conference=self.current_conf)
        expected_string = (
            '<span class="shadow-red"><b>%s</b></span>'
            ) % self.paid_vendor.b_title
        bpt_event_id = make_vendor_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)
        self.assertNotContains(response, "%d/%s" % (
            self.profile.user_object.id,
            bpt_event_id))
        self.assertContains(response, "Fee has been paid, submit NOW!")
