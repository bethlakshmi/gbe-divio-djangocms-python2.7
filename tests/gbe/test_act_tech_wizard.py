from django.core.urlresolvers import reverse
from django.core.files import File
from django.test import TestCase
from django.test import Client
from django.db.models import Max
from tests.factories.gbe_factories import (
    PersonaFactory,
    UserFactory,
)
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    login_as,
)
from gbetext import (
    default_act_tech_basic_submit,
    default_rehearsal_booked,
    rehearsal_book_error,
)
from django.utils.formats import date_format
from settings import GBE_DATETIME_FORMAT
from datetime import timedelta
from scheduler.models import (
    ActResource,
    ResourceAllocation,
)


class TestActTechWizard(TestCase):
    '''Tests for edit_act_techinfo view'''
    view_name = 'act_tech_wizard'

    def setUp(self):
        self.client = Client()

    def get_full_post(self, file=None):
        data = {
            'track_title': 'track title',
            'track_artist': 'artist',
            'confirm_no_music': 0,
            'duration': '00:04:10',
            'prop_setup': "I will leave props or set pieces on-stage that " +
            "will need to be cleared",
            'crew_instruct': 'Crew Instructions',
            'introduction_text': 'intro act',
            'read_exact': True,
            'pronouns': 'she/her',
            'feel_of_act': "*I'll* feel your act. Heh.",
            'primary_color': "Blush",
            'secondary_color': "Bashful",
            'follow_spot': True,
            'starting_position': "Onstage",
            }
        if file:
            data['track'] = file
        return data

    def check_second_stage(self, response, artist, title, selected_rehearsal):
        self.assertContains(response, "Change Rehearsal")
        assert_option_state(
            response,
            str(selected_rehearsal.id),
            date_format(selected_rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.assertContains(response, "Provide Technical Information")
        self.assertContains(response, artist)
        self.assertContains(response, title)
        self.assertContains(
            response,
            "Current Rehearsal Reservation: %s, at %s" % (
                str(selected_rehearsal),
                selected_rehearsal.starttime.strftime(GBE_DATETIME_FORMAT)))

    def test_edit_act_techinfo_unauthorized_user(self):
        context = ActTechInfoContext()
        random_performer = PersonaFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(random_performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_edit_act_techinfo_authorized_user(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            "Technical Info for %s" % context.act.b_title)
        self.assertContains(response, "Booked for: %s" % context.show.e_title)

    def test_get_act_techinfo_no_profile(self):
        context = ActTechInfoContext()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response,
                             reverse("profile_update", urlconf="gbe.urls"))

    def test_post_rehearsal_no_profile(self):
        context = ActTechInfoContext()
        extra_rehearsal = context._schedule_rehearsal(context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        data = {'book': "Book Rehearsal"}
        data['%d-rehearsal' % context.sched_event.pk] = extra_rehearsal.pk
        login_as(UserFactory(), self)
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response,
                             reverse("profile_update", urlconf="gbe.urls"))

    def test_edit_act_techinfo_rehearsal_ready(self):
        context = ActTechInfoContext()
        rehearsal = context._schedule_rehearsal(context.sched_event)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(response, "Set Rehearsal Time")
        assert_option_state(
            response,
            str(rehearsal.id),
            date_format(rehearsal.starttime, "TIME_FORMAT"))
        self.assertNotContains(response, "Provide Technical Information")

    def test_edit_act_techinfo_with_rehearsal(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        assert_option_state(
            response,
            str(context.rehearsal.id),
            date_format(context.rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.check_second_stage(response,
                                context.act.tech.track_artist,
                                context.act.tech.track_title,
                                context.rehearsal)
        self.assertContains(response,
                            'name="%d-booking_id"' % context.sched_event.pk)

    def test_edit_act_techinfo_w_prop_settings(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        assert_option_state(
            response,
            str(context.rehearsal.id),
            date_format(context.rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.check_second_stage(response,
                                context.act.tech.track_artist,
                                context.act.tech.track_title,
                                context.rehearsal)
        self.assertContains(
            response,
            '<input type="checkbox" name="prop_setup" value="I have props '
            'I will need set before my number" checked '
            'id="id_prop_setup_1" />')

    def test_book_rehearsal_and_exit(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        extra_rehearsal = context._schedule_rehearsal(context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = {'book': "Book Rehearsal"}
        data['%d-rehearsal' % context.sched_event.pk] = extra_rehearsal.pk
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        success_msg = "%s  Rehearsal Name:  %s, Start Time: %s" % (
            default_rehearsal_booked,
            str(extra_rehearsal),
            extra_rehearsal.starttime.strftime(GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response, 'success', 'Success', success_msg)

    def test_book_bad_rehearsal(self):
        context = ActTechInfoContext()
        extra_rehearsal = context._schedule_rehearsal(context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = {'book': "Book Rehearsal"}
        data['%d-rehearsal' % context.sched_event.pk] = extra_rehearsal.pk + 5
        response = self.client.post(url, data, follow=True)
        self.assertNotContains(response, default_rehearsal_booked)
        self.assertContains(response, "Select a valid choice.")
        self.assertContains(response, "Set Rehearsal Time")
        self.assertNotContains(response, "Provide Technical Information")

    def test_book_rehearsal_and_continue(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.save()
        extra_rehearsal = context._schedule_rehearsal(context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = {'book_continue': "Book & Continue"}
        data['%d-rehearsal' % context.sched_event.pk] = extra_rehearsal.pk
        resources = ActResource.objects.filter(_item=context.act.actitem_ptr)
        alloc = ResourceAllocation.objects.get(
            event=context.rehearsal,
            resource__in=resources)
        data['%d-booking_id' % context.sched_event.pk] = alloc.pk
        response = self.client.post(url, data)
        success_msg = "%s  Rehearsal Name:  %s, Start Time: %s" % (
            default_rehearsal_booked,
            str(extra_rehearsal),
            extra_rehearsal.starttime.strftime(GBE_DATETIME_FORMAT))
        assert_alert_exists(
            response, 'success', 'Success', success_msg)
        self.assertContains(response,
                            'name="%d-booking_id"' % context.sched_event.pk)
        self.check_second_stage(response,
                                context.act.tech.track_artist,
                                context.act.tech.track_title,
                                extra_rehearsal)
        self.assertContains(
            response,
            '<input type="checkbox" name="prop_setup" value="I have props '
            'I will need set before my number" checked '
            'id="id_prop_setup_1" />')
        resources = ActResource.objects.filter(_item=context.act.actitem_ptr)
        alloc = ResourceAllocation.objects.filter(
            resource__in=resources)
        self.assertEqual(alloc.count(), 2)

    def test_bad_booking_id(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.save()
        extra_rehearsal = context._schedule_rehearsal(context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = {'book_continue': "Book & Continue"}
        data['%d-rehearsal' % context.sched_event.pk] = extra_rehearsal.pk
        alloc = ResourceAllocation.objects.aggregate(Max('pk'))['pk__max']+1
        data['%d-booking_id' % context.sched_event.pk] = alloc
        response = self.client.post(url, data)
        self.assertContains(response, rehearsal_book_error)

    def test_edit_act_w_bad_tech_info(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = self.get_full_post()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.check_second_stage(response,
                                data['track_artist'],
                                data['track_title'],
                                context.rehearsal)
        self.assertContains(
            response,
            'Incomplete Audio Info - please either provide Track '
            'Title, Artist and the audio file, or confirm that '
            'there is no music.')

    def test_edit_act_w_audio_file(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        filename = open("tests/gbe/gbe_pagebanner.png", 'r')
        file = File(filename)
        data = self.get_full_post(file)
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'success', 'Success', default_act_tech_basic_submit)

    def test_edit_act_wout_music(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = self.get_full_post()
        data['confirm_no_music'] = 1
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'success', 'Success', default_act_tech_basic_submit)
