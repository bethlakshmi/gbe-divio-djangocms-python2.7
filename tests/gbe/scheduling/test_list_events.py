from django.test import (
    TestCase,
    Client
)
from django.core.urlresolvers import reverse
from tests.functions.gbe_functions import (
    clear_conferences,
    login_as,
)
from tests.factories.gbe_factories import (
    ConferenceFactory,
    ClassFactory,
    ProfileFactory,
    ShowFactory,
    GenericEventFactory,
)
from tests.contexts import (
    ClassContext,
    ShowContext,
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
        self.assertTrue(this_class.e_title in response.content)
        self.assertFalse(that_class.e_title in response.content)

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
        self.assertTrue(generic_event.e_title in response.content)
        self.assertTrue(show.e_title in response.content)
        self.assertTrue(accepted_class.e_title in response.content)
        self.assertFalse(rejected_class.e_title in response.content)
        self.assertFalse(previous_class.e_title in response.content)

    def test_no_avail_conf(self):
        clear_conferences()
        login_as(ProfileFactory(), self)
        response = self.client.get(
            reverse("event_list",
                    urlconf="gbe.scheduling.urls"))
        self.assertEqual(404, response.status_code)

    def test_view_list_event_type_not_case_sensitive(self):
        param = 'class'
        url_lower = reverse("event_list",
                            urlconf="gbe.scheduling.urls",
                            args=[param.lower()])

        url_upper = reverse("event_list",
                            urlconf="gbe.scheduling.urls",
                            args=[param.upper()])

        assert (self.client.get(url_lower).content ==
                self.client.get(url_upper).content)

    def test_view_list_event_type_not_in_list_titles(self):
        param = 'classification'
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=[param])
        response = self.client.get(url)
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
        self.assertFalse(show.e_title in response.content)
        self.assertTrue(accepted_class.e_title in response.content)

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

    def test_not_really_interested_in_event(self):
        context = ShowContext(conference=self.conf)
        interested_profile = ProfileFactory()
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=['Show'])
        login_as(interested_profile, self)
        response = self.client.get(url)
        set_fav_link = reverse(
            "set_favorite",
            args=[context.sched_event.pk, "on"],
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
        self.assertContains(response,
                            '<a href="#" class="detail_link-disabled')
        self.assertNotContains(response, "fa-tachometer")

    def test_interest_not_shown(self):
        old_conf = ConferenceFactory(status="completed")
        context = ShowContext(
            conference=old_conf)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Show"])
        response = self.client.get(
            url,
            data={"conference": old_conf.conference_slug})
        login_as(context.performer.performer_profile, self)
        response = self.client.get(url)
        self.assertNotContains(response, 'fa-star')
        self.assertNotContains(response, 'fa-star-o')

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
        generic_event = GenericEventFactory(e_conference=self.conf,
                                            type="Volunteer")
        login_as(ProfileFactory(), self)
        url = reverse("event_list",
                      urlconf="gbe.scheduling.urls",
                      args=["Volunteer"])
        response = self.client.get(
            url,
            data={"conference": self.conf.conference_slug})
        self.assertContains(response, generic_event.e_title)
        self.assertNotContains(response, this_class.e_title)
        self.assertNotContains(response, 'fa-star')
        self.assertNotContains(response, 'fa-star-o')

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
