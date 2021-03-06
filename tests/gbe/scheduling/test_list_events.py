from django.test import (
    TestCase,
    Client
)
from django.urls import reverse
from tests.functions.gbe_functions import (
    clear_conferences,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    PersonaFactory,
    ProfileFactory,
    ShowFactory,
    GenericEventFactory,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
    StaffAreaContext,
)
from datetime import (
    datetime,
    timedelta,
)


class TestViewList(TestCase):

    def setUp(self):
        clear_conferences()
        self.client = Client()
        self.conf = ConferenceFactory()

    def test_view_list_given_slug(self):
        other_conf = ConferenceFactory()
        this_class = ClassFactory.create(accepted=3,
                                         e_conference=self.conf,
                                         b_conference=self.conf)
        that_class = ClassFactory.create(accepted=3,
                                         e_conference=other_conf,
                                         b_conference=other_conf)
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Class"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, this_class.e_title)
        self.assertNotContains(response, that_class.e_title)

    def test_view_list_default_view_current_conf_exists(self):
        '''
        /scheduler/view_list/ should return all events in the current
        conference, assuming a current conference exists
        '''
        other_conf = ConferenceFactory(status='completed')
        show = ShowFactory(e_conference=self.conf)
        generic_event = GenericEventFactory(e_conference=self.conf)
        accepted_class = ClassFactory(accepted=3,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        previous_class = ClassFactory(accepted=3,
                                      e_conference=other_conf,
                                      b_conference=other_conf)
        rejected_class = ClassFactory(accepted=1,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertContains(response, generic_event.e_title)
        self.assertContains(response, show.e_title)
        self.assertContains(response, accepted_class.e_title)
        self.assertNotContains(response, rejected_class.e_title)
        self.assertNotContains(response, previous_class.e_title)

    def test_no_avail_conf(self):
        clear_conferences()
        login_as(ProfileFactory(), self)
        response = self.client.get(
            reverse("event_list",
                    urlconf="gbe.scheduling.urls"),
            follow=True)
        self.assertEqual(404, response.status_code)

    def test_view_list_event_type_not_in_list_titles(self):
        param = 'classification'
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=[param])
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_view_list_only_classes(self):
        '''
        /scheduler/view_list/ should return all events in the current
        conference, assuming a current conference exists
        '''
        show = ShowFactory(e_conference=self.conf)
        generic_event = GenericEventFactory(e_conference=self.conf)
        accepted_class = ClassFactory(accepted=3,
                                      e_conference=self.conf,
                                      b_conference=self.conf)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertNotContains(response, show.e_title)
        self.assertNotContains(response, generic_event.e_title)
        self.assertContains(response, accepted_class.e_title)

        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['class'])
        response = self.client.get(url)
        self.assertNotContains(response, show.e_title)
        self.assertNotContains(response, generic_event.e_title)
        self.assertContains(response, accepted_class.e_title)

    def test_interested_in_event(self):
        context = ShowContext(conference=self.conf)
        interested_profile = context.set_interest()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Show'])
        login_as(interested_profile, self)
        response = self.client.get(url)
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "off"],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            set_fav_link,
            url))

    def test_disabled_interest(self):
        context = ClassContext(conference=self.conf,
                               starttime=datetime.now()-timedelta(days=1))
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        login_as(context.teacher.performer_profile, self)
        response = self.client.get(url)
        self.assertContains(
          response,
          '<a href="#" class="cal-favorite detail_link-disabled')
        self.assertNotContains(response, "fa-tachometer")

    def test_booked_teacher_over_bid_teacher(self):
        context = ClassContext(conference=self.conf,
                               starttime=datetime.now()-timedelta(days=1))
        context.bid.teacher = PersonaFactory()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        login_as(context.teacher.performer_profile, self)
        response = self.client.get(url)
        self.assertContains(response, str(context.teacher.performer))
        self.assertNotContains(response, str(context.bid.teacher.performer))

    def test_view_panels(self):
        this_class = ClassFactory.create(accepted=3,
                                         e_conference=self.conf,
                                         b_conference=self.conf,
                                         type="Panel")
        that_class = ClassFactory.create(accepted=3,
                                         e_conference=self.conf,
                                         b_conference=self.conf)
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Panel"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, this_class.e_title)
        self.assertNotContains(response, that_class.e_title)
        self.assertContains(response, this_class.teacher.name)

    def test_view_volunteers(self):
        this_class = ClassFactory.create(accepted=3,
                                         e_conference=self.conf,
                                         b_conference=self.conf)
        staff_context = StaffAreaContext(conference=self.conf)
        opportunity = staff_context.add_volunteer_opp()
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'on'],
                           urlconf='gbe.scheduling.urls')
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(response, vol_link)
        self.assertContains(response,
                            'volunteered.gif" class="volunteer-icon"')
        self.assertNotContains(response, this_class.e_title)
        self.assertNotContains(response, 'fa-star')
        self.assertNotContains(response, 'fa-star-o')

    def test_view_volunteer_filled(self):
        staff_context = StaffAreaContext(conference=self.conf)
        volunteer, booking = staff_context.book_volunteer()
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.max_volunteers = 1
        opportunity.save()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'on'],
                           urlconf='gbe.scheduling.urls')
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(
          response,
          'This event has all the volunteers it needs.')

    def test_view_volunteers_past_event(self):
        staff_context = StaffAreaContext(conference=self.conf)
        opportunity = staff_context.add_volunteer_opp()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'on'],
                           urlconf='gbe.scheduling.urls')
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertNotContains(response, vol_link)
        self.assertNotContains(response, 'class="volunteer-icon"')

    def test_view_volunteers_approval_pending(self):
        context = StaffAreaContext(conference=self.conf)
        volunteer, booking = context.book_volunteer(role="Pending Volunteer")
        opportunity = booking.event
        opportunity.approval_needed = True
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(volunteer, self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        vol_link = reverse('set_volunteer',
                           args=[opportunity.pk, 'off'],
                           urlconf='gbe.scheduling.urls')
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(response, vol_link)
        self.assertContains(response, 'awaiting_approval.gif')

    def test_view_volunteers_rejected(self):
        context = StaffAreaContext(conference=self.conf)
        volunteer, booking = context.book_volunteer(role="Rejected")
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(volunteer, self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(response, "You were not accepted for this shift.")

    def test_view_volunteers_already_committed(self):
        context = StaffAreaContext(conference=self.conf)
        volunteer, booking = context.book_volunteer(role="Teacher")
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(volunteer, self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(response, 'You are a teacher')

    def test_view_volunteers_waitlisted(self):
        context = StaffAreaContext(conference=self.conf)
        volunteer, booking = context.book_volunteer(role="Waitlisted")
        opportunity = booking.event
        opportunity.starttime = datetime.now() + timedelta(days=1)
        opportunity.save()
        login_as(volunteer, self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, opportunity.eventitem.e_title)
        self.assertContains(response, "You were waitlisted for this shift.")

    def test_disabled_eval(self):
        context = ClassContext(conference=self.conf,
                               starttime=datetime.now()-timedelta(days=1))
        eval_profile = context.set_eval_answerer()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        login_as(eval_profile, self)
        response = self.client.get(url)
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertNotContains(response, "%s?next=%s" % (
            eval_link,
            url))
        self.assertContains(response, "You have already rated this class")

    def test_eval_ready(self):
        context = ClassContext(conference=self.conf,
                               starttime=datetime.now()-timedelta(days=1))
        context.setup_eval()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        response = self.client.get(url)
        eval_link = reverse(
            "eval_event",
            args=[context.sched_event.pk, ],
            urlconf="gbe.scheduling.urls")
        self.assertContains(response, "%s?next=%s" % (
            eval_link,
            url))

    def test_eval_future(self):
        context = ClassContext(conference=self.conf,
                               starttime=datetime.now()+timedelta(days=1))
        context.setup_eval()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Class'])
        response = self.client.get(url)
        self.assertNotContains(response, "fa-tachometer")
