from django.test import TestCase
from datetime import datetime
import pytz
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import(
    ActFactory,
    BioFactory,
    ClassFactory,
    ConferenceFactory,
    CostumeFactory,
    FlexibleEvaluationFactory,
    ProfileFactory,
    TechInfoFactory,
    UserFactory,
    VendorFactory,
)
from tests.factories.scheduler_factories import (
    EventLabelFactory,
    SchedEventFactory,
    PeopleAllocationFactory,
)
from tests.factories.ticketing_factories import RoleEligibilityConditionFactory
from ticketing.models import Signature
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
    set_image,
    make_vendor_app_purchase,
    make_vendor_app_ticket,
    make_act_app_ticket,
    make_act_app_purchase,
)
from tests.functions.scheduler_functions import (
    get_or_create_bio,
    get_or_create_profile,
)
from tests.functions.ticketing_functions import set_form
from tests.contexts import (
    ActTechInfoContext,
    ClassContext,
    StaffAreaContext,
    VolunteerContext,
)
from django.utils.formats import date_format
from gbetext import (
    interested_explain_msg,
    SCHEDULE_REHEARSAL
)
from datetime import (
    datetime,
    timedelta,
)
from django.core.files.uploadedfile import SimpleUploadedFile
from easy_thumbnails.files import get_thumbnailer


class TestIndex(TestCase):
    '''Tests for index view'''
    view_name = 'home'

    @classmethod
    def setUpTestData(cls):
        cls.current_conf = ConferenceFactory(status='upcoming')
        cls.previous_conf = ConferenceFactory(accepting_bids="[]",
                                              status='completed')

        # User/Human setup
        cls.profile = ProfileFactory()
        cls.performer = BioFactory(contact=cls.profile,
                                   label="Test Index Label")
        # Bid types previous and current
        cls.current_act = ActFactory(bio=cls.performer,
                                     submitted=True,
                                     b_conference=cls.current_conf)
        cls.previous_act = ActFactory(bio=cls.performer,
                                      submitted=True,
                                      b_conference=cls.previous_conf)
        cls.current_class = ClassFactory(teacher_bio=cls.performer,
                                         submitted=True,
                                         accepted=3,
                                         b_conference=cls.current_conf)
        cls.previous_class = ClassFactory(teacher_bio=cls.performer,
                                          submitted=True,
                                          accepted=3,
                                          b_conference=cls.previous_conf)

        cls.current_vendor = VendorFactory(
            business__owners=[cls.profile],
            submitted=True,
            b_conference=cls.current_conf)
        cls.previous_vendor = VendorFactory(
            business__owners=[cls.profile],
            submitted=True,
            b_conference=cls.previous_conf)

        cls.current_costume = CostumeFactory(
            profile=cls.profile,
            submitted=True,
            b_conference=cls.current_conf)
        cls.previous_costume = CostumeFactory(
            profile=cls.profile,
            submitted=True,
            b_conference=cls.previous_conf)

        # Event assignments, previous and current
        cls.current_sched = SchedEventFactory(
            event_style='Volunteer',
            starttime=datetime(2016, 2, 5, 12, 30, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=cls.current_sched,
                          text=cls.current_conf.conference_slug)
        cls.previous_sched = SchedEventFactory(
            event_style='Special',
            starttime=datetime(2015, 2, 25, 12, 30, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=cls.previous_sched,
                          text=cls.previous_conf.conference_slug)

        cls.current_class_sched = SchedEventFactory(
            connected_id=cls.current_class.pk,
            connected_class=cls.current_class.__class__.__name__,
            starttime=datetime(2016, 2, 5, 2, 30, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=cls.current_class_sched,
                          text=cls.current_conf.conference_slug)
        cls.previous_class_sched = SchedEventFactory(
            connected_id=cls.previous_class.pk,
            connected_class=cls.previous_class.__class__.__name__,
            starttime=datetime(2015, 2, 25, 2, 30, 0, 0),
            max_volunteer=10)
        EventLabelFactory(event=cls.previous_class_sched,
                          text=cls.previous_conf.conference_slug)

        people = get_or_create_profile(cls.profile)
        for schedule_item in [cls.current_sched,
                              cls.previous_sched]:
            volunteer_assignment = PeopleAllocationFactory(
                event=schedule_item,
                people=people,
                label="Landing_Page_Test",
                role='Volunteer',
            )

        people = get_or_create_bio(cls.performer)
        for schedule_item in [cls.current_class_sched,
                              cls.previous_class_sched]:
            volunteer_assignment = PeopleAllocationFactory(
                event=schedule_item,
                people=people,
                role='Teacher',
            )
        cls.condition = RoleEligibilityConditionFactory(
            role="Teacher",
            checklistitem__description="Landing page sign!",
            checklistitem__e_sign_this=set_form())

    def setUp(self):
        self.client = Client()

    def assert_event_is_present(self, response, event):
        ''' test all parts of the event being on the landing page schedule'''
        self.assertContains(response, event.title)
        self.assertContains(response,
                            date_format(event.start_time, "DATETIME_FORMAT"))
        self.assertContains(response, reverse(
            'detail_view',
            urlconf="gbe.scheduling.urls",
            args=[event.pk]))

    def assert_event_is_not_present(self, response, event):
        ''' test all parts of the event being on the landing page schedule'''
        self.assertNotContains(response, event.title)
        self.assertNotContains(
            response,
            date_format(event.start_time, "DATETIME_FORMAT"))
        self.assertNotContains(response, reverse(
            'detail_view',
            urlconf="gbe.scheduling.urls",
            args=[event.pk]))

    def get_landing_page(self):
        self.url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        return self.client.get(self.url)

    def test_no_profile(self):
        url = reverse('home', urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response, '%s?next=%s' % (
            reverse('profile_update', urlconf="gbe.urls"),
            url))

    def test_landing_page_path(self):
        '''Basic test of landing_page view
        '''
        response = self.get_landing_page()
        self.assertEqual(response.status_code, 200)
        content = str(response.content, 'utf-8')
        does_not_show_previous = (
            self.previous_act.b_title not in content and
            self.previous_class.b_title not in content and
            "%s - %s" % (
                self.previous_vendor.business.name,
                self.previous_conf.conference_slug) not in content and
            self.previous_costume.b_title not in content)
        shows_all_current = (
            self.current_act.b_title in content and
            self.current_class.b_title in content and
            "%s - %s" % (
                self.current_vendor.business.name,
                self.current_conf.conference_slug) in content and
            self.current_costume.b_title in content)
        assert does_not_show_previous
        assert shows_all_current
        self.assertContains(response, "Apply to Perform")
        self.assertContains(response, "Apply to Teach")
        self.assertContains(response, "Volunteer")
        self.assert_event_is_present(response, self.current_sched)
        self.assert_event_is_not_present(response, self.previous_sched)
        self.assert_event_is_present(response, self.current_class_sched)
        self.assert_event_is_not_present(response, self.previous_class_sched)
        self.assertNotContains(response, "text-danger")
        self.assertContains(response, reverse(
            "volunteer_signup",
            urlconf="gbe.scheduling.urls"))
        self.assertContains(response, reverse("sign_forms",
                                              urlconf='ticketing.urls'))

    def test_conf_not_accepting_bids(self):
        # No apply buttons when bidding is off
        orig_state = self.current_conf.accepting_bids
        self.current_conf.accepting_bids = "[]"
        self.current_conf.save()
        response = self.get_landing_page()
        self.assertNotContains(response, "Apply to Perform")
        self.assertNotContains(response, "Apply to Teach")
        self.assertNotContains(response, "Volunteer")
        self.current_conf.accepting_bids = orig_state
        self.current_conf.save()

    def test_historical_view(self):
        sig = Signature(user=self.profile.user_object,
                        name_signed="Signed Name",
                        conference=self.current_conf,
                        signed_file=self.condition.checklistitem.e_sign_this)
        sig.save()
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(
            url,
            data={'historical': 1})
        content = str(response.content, 'utf-8')
        self.assertEqual(response.status_code, 200)
        shows_all_previous = (
            self.previous_act.b_title in content and
            self.previous_class.b_title in content and
            "%s - %s" % (
                self.previous_vendor.business.name,
                self.previous_conf.conference_slug) in content and
            self.previous_costume.b_title in content in content)
        does_not_show_current = (
            self.current_act.b_title not in content and
            self.current_class.b_title not in content and
            "%s - %s" % (
                self.current_vendor.business.name,
                self.current_conf.conference_slug) not in content and
            self.current_costume.b_title not in content)
        assert shows_all_previous
        assert does_not_show_current
        self.assert_event_is_present(response, self.previous_sched)
        self.assert_event_is_not_present(response, self.current_sched)
        self.assert_event_is_present(response, self.previous_class_sched)
        self.assert_event_is_not_present(response, self.current_class_sched)
        self.assertNotContains(response, reverse("sign_forms",
                                                 urlconf='ticketing.urls'))

    def test_as_privileged_user(self):
        staff_profile = ProfileFactory()
        grant_privilege(staff_profile, "Ticketing - Admin")
        login_as(staff_profile, self)
        url = reverse('admin_landing_page', urlconf='gbe.urls',
                      args=[staff_profile.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are viewing a")

    def test_acts_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Act Reviewers")
        login_as(staff_profile, self)
        reviewed_act = ActFactory(submitted=True,
                                  b_conference=self.current_conf)
        FlexibleEvaluationFactory(bid=reviewed_act,
                                  evaluator=staff_profile)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertContains(response, 'Act:  1 out of 2')
        self.assertContains(response,
                            reverse('act_review_list', urlconf='gbe.urls'))

    def test_classes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Class Reviewers")
        login_as(staff_profile, self)
        klass = ClassFactory(submitted=True,
                             b_conference=self.current_conf)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertContains(response, 'Class:  1 out of 1')
        self.assertContains(response,
                            reverse('class_review_list', urlconf='gbe.urls'))

    def test_vendors_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Vendor Reviewers")
        login_as(staff_profile, self)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertContains(response, 'Vendor:  1 out of 1')
        self.assertContains(response,
                            reverse('vendor_review_list', urlconf='gbe.urls'))

    def test_costumes_to_review(self):
        staff_profile = ProfileFactory(user_object__is_staff=True)
        grant_privilege(staff_profile, "Costume Reviewers")
        login_as(staff_profile, self)
        url = reverse('home', urlconf='gbe.urls')
        response = self.client.get(url)
        self.assertContains(response, 'Costume:  1 out of 1')
        self.assertContains(response,
                            reverse('costume_review_list', urlconf='gbe.urls'))

    def test_profile_image(self):
        set_image(self.performer)
        response = self.get_landing_page()
        self.assertContains(response, self.performer.name)
        self.assertContains(response, self.performer.label)
        self.assertContains(
            response,
            get_thumbnailer(self.performer.img).get_thumbnail(
                {'size': (20, 20), 'crop': True, 'upscale': True}).url)

    def test_cannot_edit_troupe_if_not_contact(self):
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        member = ProfileFactory()
        people.users.add(member.user_object)
        url = reverse("home", urlconf="gbe.urls")
        login_as(member, self)
        response = self.client.get(url)
        self.assertContains(response, "(Click to edit)", 0)

    def test_review_act_w_troupe(self):
        # causes a check on act complete state that is different from soloist
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        member = ProfileFactory()
        people.users.add(member.user_object)
        act = ActFactory(bio=troupe,
                         submitted=True,
                         b_conference=self.current_conf)
        login_as(member, self)
        url = reverse("home", urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertContains(response, act.b_title)

    def test_act_tech_troupe_member_view(self):
        troupe = BioFactory(multiple_performers=True)
        people = get_or_create_bio(troupe)
        member = ProfileFactory()
        people.users.add(member.user_object)
        act = ActFactory(bio=troupe,
                         submitted=True,
                         b_conference=self.current_conf,
                         accepted=3)
        current_act_context = ActTechInfoContext(
            performer=troupe,
            act=act,
            conference=self.current_conf,
            schedule_rehearsal=True)
        act.tech = TechInfoFactory(
            track_artist="",
            track=SimpleUploadedFile("file.mp3", b"file_content"),
            prop_setup="text",
            starting_position="Onstage",
            primary_color="text",
            feel_of_act="text",
            introduction_text="text")
        act.tech.save()
        event_id = make_act_app_ticket(self.current_conf)
        login_as(member, self)
        url = reverse("home", urlconf="gbe.urls")
        response = self.client.get(url)
        self.assertContains(
            response,
            reverse("act_techinfo_detail",
                    urlconf="gbe.reporting.urls",
                    args=[act.pk]))

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
            sched_event=current_act_context.sched_event)
        self.current_act.accepted = 3
        self.current_act.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            second_act_context.act.b_title,
                            count=3)
        self.assertContains(response,
                            current_act_context.act.b_title,
                            count=3)
        self.assertContains(response,
                            second_act_context.sched_event.title,
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
            teacher=BioFactory(contact=self.profile))
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
            teacher=BioFactory(contact=self.profile))
        interested = []
        for i in range(0, 3):
            interested += [context.set_interest()]
        url = reverse('home', urlconf='gbe.urls')
        login_as(self.profile, self)
        response = self.client.get(
            url,
            data={'historical': 1})
        for person in interested:
            self.assertNotContains(
                response,
                "%s &lt;%s&gt;;<br>" % (person.display_name,
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
        self.unpaid_act = ActFactory(bio=self.performer,
                                     submitted=False,
                                     b_conference=self.current_conf)
        expected_string = (
            '<b>%s</b></span> - Not submitted'
            ) % self.unpaid_act.b_title
        event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)

    def test_paid_act_draft(self):
        make_act_app_purchase(self.current_conf,
                              self.profile.user_object)
        make_act_app_purchase(self.current_conf,
                              self.profile.user_object)
        self.paid_act = ActFactory(bio=self.performer,
                                   submitted=False,
                                   b_conference=self.current_conf)
        event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, "Fee has been paid, submit NOW!")

    def test_unpaid_vendor_draft(self):
        self.unpaid_vendor = VendorFactory(
            business__owners=[self.profile],
            submitted=False,
            b_conference=self.current_conf)
        expected_string = (
            '<i class="fas fa-arrow-alt-circle-right"></i> <b>%s - %s</b>'
            ) % (self.unpaid_vendor.business.name,
                 self.current_conf.conference_slug)
        event_id = make_vendor_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)

    def test_paid_vendor_draft(self):
        make_vendor_app_purchase(self.current_conf,
                                 self.profile.user_object)
        make_vendor_app_purchase(self.current_conf,
                                 self.profile.user_object)
        self.paid_vendor = VendorFactory(
            business__owners=[self.profile],
            submitted=False,
            b_conference=self.current_conf)
        expected_string = (
            '<i class="fas fa-arrow-alt-circle-right"></i> <b>%s - %s</b>'
            ) % (self.paid_vendor.business.name,
                 self.current_conf.conference_slug)
        event_id = make_vendor_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(response, expected_string)
        self.assertNotContains(response, "%d/%s" % (
            self.profile.user_object.id,
            event_id))
        self.assertContains(response, "Fee has been paid, submit NOW!")

    def test_act_tech_alert(self):
        current_act_context = ActTechInfoContext(
            performer=self.performer,
            act=self.current_act,
            conference=self.current_conf,
            schedule_rehearsal=True)
        self.current_act.tech.track_artist = ""
        self.current_act.tech.save()
        self.current_act.accepted = 3
        self.current_act.save()
        event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertContains(
            response,
            SCHEDULE_REHEARSAL % (
                self.current_act.b_title,
                reverse('act_tech_wizard',
                        urlconf='gbe.urls',
                        args=[self.current_act.id])))

    def test_stage_manager_button(self):
        self.context = ActTechInfoContext(schedule_rehearsal=True)
        self.profile = self.context.make_priv_role()
        response = self.get_landing_page()
        self.assertContains(response, reverse(
            'show_dashboard',
            urlconf='gbe.scheduling.urls',
            args=[self.context.sched_event.pk]))

    def test_staff_lead_button(self):
        show_context = ActTechInfoContext(schedule_rehearsal=True)
        show_context.sched_event.slug = "Iamashowslug"
        show_context.sched_event.save()
        vol_context = VolunteerContext(sched_event=show_context.sched_event)
        context = StaffAreaContext(conference=show_context.conference)
        EventLabelFactory(event=vol_context.opp_event,
                          text=context.area.slug)
        vol1, opp1 = context.book_volunteer(
            volunteer_sched_event=vol_context.opp_event,
            volunteer=context.staff_lead)
        self.profile = context.staff_lead

        response = self.get_landing_page()
        self.assertContains(response, reverse(
            'show_dashboard',
            urlconf='gbe.scheduling.urls',
            args=[show_context.sched_event.pk]))
        self.assertContains(
            response,
            "%s: %s" % (show_context.sched_event.title,
                        vol_context.opp_event.title))
        self.assertContains(
            response,
            "%s: %s" % (show_context.sched_event.slug,
                        vol_context.opp_event.title))

    def test_no_act_tech_alert(self):
        current_act_context = ActTechInfoContext(
            performer=self.performer,
            act=self.current_act,
            conference=self.current_conf,
            schedule_rehearsal=True)
        self.current_act.tech = TechInfoFactory(
            track_artist="",
            track=SimpleUploadedFile("file.mp3", b"file_content"),
            prop_setup="text",
            starting_position="Onstage",
            primary_color="text",
            feel_of_act="text",
            introduction_text="text")
        self.current_act.accepted = 3
        self.current_act.save()
        event_id = make_act_app_ticket(self.current_conf)
        response = self.get_landing_page()
        self.assertNotContains(
            response,
            SCHEDULE_REHEARSAL % (
                self.current_act.b_title,
                reverse('act_tech_wizard',
                        urlconf='gbe.urls',
                        args=[self.current_act.id])))
