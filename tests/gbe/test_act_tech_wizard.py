from django.urls import reverse
from django.test import TestCase
from django.test import Client
from django.db.models import Max
from tests.factories.gbe_factories import (
    ActFactory,
    BioFactory,
    UserFactory,
)
from tests.contexts import ActTechInfoContext
from tests.gbe.test_gbe import TestGBE
from tests.functions.gbe_functions import (
    assert_alert_exists,
    assert_option_state,
    login_as,
)
from gbetext import (
    default_act_tech_advanced_submit,
    default_act_tech_basic_submit,
    default_rehearsal_booked,
    mic_options,
    rehearsal_book_error,
    rehearsal_remove_confirmation,
)
from django.utils.formats import date_format
from settings import GBE_DATETIME_FORMAT
from datetime import timedelta
from gbe.models import (
    Act,
    Bio,
)
from scheduler.models import (
    PeopleAllocation,
)


class TestActTechWizard(TestGBE):
    '''Tests for edit_act_techinfo view'''
    view_name = 'act_tech_wizard'

    @classmethod
    def setUpTestData(cls):
        cls.context = ActTechInfoContext()

    def setUp(self):
        self.client = Client()

    def get_full_post(self, file=None):
        data = {
            'track_title': 'track title',
            'track_artist': '',
            'confirm_no_music': 0,
            'duration': '00:04:10',
            'prop_setup': "I will leave props or set pieces on-stage that " +
            "will need to be cleared",
            'crew_instruct': 'Crew Instructions',
            'introduction_text': 'intro act',
            'read_exact': True,
            'pronouns_0': 'she/her',
            'feel_of_act': "*I'll* feel your act. Heh.",
            'primary_color': "Blush",
            'secondary_color': "Bashful",
            'follow_spot': True,
            'starting_position': "Onstage",
            'finish_basics': "Complete Form"
            }
        if file:
            data['track'] = file
        return data

    def check_second_stage(self, response, title, selected_rehearsal):
        self.assertContains(response, "Change Rehearsal")
        assert_option_state(
            response,
            str(selected_rehearsal.id),
            date_format(selected_rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.assertContains(response, "Provide Technical Information")
        self.assertContains(response, title)
        self.assertContains(
            response,
            "Current Rehearsal Reservation: %s, at %s" % (
                str(selected_rehearsal),
                selected_rehearsal.starttime.strftime(GBE_DATETIME_FORMAT)))

    def test_edit_act_techinfo_unauthorized_user(self):
        random_performer = BioFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        login_as(random_performer.contact, self)
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

    def test_edit_act_techinfo_authorized_user(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        login_as(self.context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(
            response,
            "Technical Info for %s" % self.context.act.b_title)
        self.assertContains(response,
                            "Booked for: %s" % self.context.sched_event.title)

    def test_edit_act_techinfo_get_bad_act(self):
        bad_act_id = Act.objects.aggregate(Max('pk'))['pk__max']+1
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[bad_act_id])
        login_as(self.context.performer.contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_edit_act_techinfo_get_unaccepted_act(self):
        act = ActFactory()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[act.pk])
        login_as(act.performer.contact, self)
        response = self.client.get(url, follow=True)
        self.assertEqual(404, response.status_code)

    def test_get_act_techinfo_no_profile(self):
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        login_as(UserFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(response,
                             reverse("profile_update", urlconf="gbe.urls"))

    def test_post_rehearsal_no_profile(self):
        extra_rehearsal = self.context._schedule_rehearsal(
            self.context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        data = {'book': "Book Rehearsal"}
        data['%d-rehearsal' % self.context.sched_event.pk] = extra_rehearsal.pk
        login_as(UserFactory(), self)
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response,
                             reverse("profile_update", urlconf="gbe.urls"))

    def test_edit_act_techinfo_rehearsal_ready(self):
        rehearsal = self.context._schedule_rehearsal(self.context.sched_event)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        login_as(self.context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(response, "Set Rehearsal Time")
        assert_option_state(
            response,
            str(rehearsal.id),
            date_format(rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.assertNotContains(response, "Provide Technical Information")
        self.assertNotContains(response,
                               'Advanced Technical Information (Optional)')

    def test_edit_no_music_rehearsal_ready(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.tech.confirm_no_music = True
        context.tech.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        assert_option_state(
            response,
            "1",
            "No, I will not need an audio track",
            True)

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
                                context.act.tech.track_title,
                                context.rehearsal)
        self.assertContains(response,
                            'name="%d-booking_id"' % context.sched_event.pk)
        assert_option_state(
            response,
            "0",
            "Yes, I will upload an audio track",
            True)
        self.assertNotContains(response,
                               'Advanced Technical Information (Optional)')

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
                                context.act.tech.track_title,
                                context.rehearsal)
        self.assertContains(
            response,
            '<input type="checkbox" name="prop_setup" value="I have props '
            'I will need set before my number" '
            'id="id_prop_setup_1" checked />',
            html=True)

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
        extra_rehearsal = self.context._schedule_rehearsal(
            self.context.sched_event)
        extra_rehearsal.starttime = extra_rehearsal.starttime - timedelta(
            hours=1)
        extra_rehearsal.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[self.context.act.pk])
        login_as(self.context.performer.contact, self)
        data = {'book': "Book Rehearsal"}
        data['%d-rehearsal' % self.context.sched_event.pk] = \
            extra_rehearsal.pk + 5
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
        alloc = PeopleAllocation.objects.get(
            event=context.rehearsal,
            ordering__class_id=context.act.pk)
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
                                context.act.tech.track_title,
                                extra_rehearsal)
        self.assertContains(
            response,
            '<input type="checkbox" name="prop_setup" value="I have props '
            'I will need set before my number" '
            'id="id_prop_setup_1" checked />',
            html=True)
        alloc = PeopleAllocation.objects.filter(
            ordering__class_id=context.act.pk)
        self.assertEqual(alloc.count(), 2)
        assert_option_state(
            response,
            "0",
            "Yes, I will upload an audio track",
            True)
        self.assertNotContains(response,
                               'Advanced Technical Information (Optional)')
        self.assert_radio_state(response,
                                'pronouns_0',
                                'id_pronouns_0_3',
                                '',
                                checked=True,
                                required=True)
        self.assertContains(
            response,
            '<input type="text" name="pronouns_1" id="id_pronouns_0">',
            html=True)

    def test_book_no_rehearsal_and_continue(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = {'book_continue': "Book & Continue"}
        data['%d-rehearsal' % context.sched_event.pk] = -1
        alloc = PeopleAllocation.objects.get(
            event=context.rehearsal,
            ordering__class_id=context.act.pk)
        data['%d-booking_id' % context.sched_event.pk] = alloc.pk
        response = self.client.post(url, data)
        self.assertTrue(Act.objects.filter(
            pk=context.act.pk,
            tech__confirm_no_rehearsal=True).exists())
        assert_alert_exists(
            response, 'success', 'Success', rehearsal_remove_confirmation)
        self.assertNotContains(response, "Current Rehearsal Reservation")
        self.assertContains(response,
                            'name="%d-booking_id"' % context.sched_event.pk)
        self.assertContains(response, "Provide Technical Information")
        assert_option_state(
            response,
            "-1",
            "No rehearsal needed",
            True)

    def test_book_rehearsal_and_continue_no_music(self):
        # in this case, the act had previously confirmed no music, check
        # that this state is cleared when rehearsal is booked.
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.confirm_no_music = True
        context.act.tech.confirm_no_rehearsal = True
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
        alloc = PeopleAllocation.objects.get(
            event=context.rehearsal,
            ordering__class_id=context.act.pk)
        data['%d-booking_id' % context.sched_event.pk] = alloc.pk
        response = self.client.post(url, data)
        assert_option_state(
            response,
            "1",
            "No, I will not need an audio track",
            True)
        self.assertTrue(Act.objects.filter(
            pk=context.act.pk,
            tech__confirm_no_rehearsal=False).exists())

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
        alloc = PeopleAllocation.objects.aggregate(Max('pk'))['pk__max']+1
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
                                data['track_title'],
                                context.rehearsal)
        self.assertContains(
            response,
            'Incomplete Audio Info - please either provide track '
            'title and the audio file, or confirm that there is no music.')
        self.assertNotContains(response,
                               "Advanced Technical Information (Optional)")

    def test_edit_act_w_audio_file(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        filename = open("tests/gbe/gbe_pagebanner.png", 'rb')
        data = self.get_full_post(filename)
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'success', 'Success', default_act_tech_basic_submit)
        reload_performer = Bio.objects.get(pk=context.performer.pk)
        self.assertEqual('she/her', reload_performer.pronouns)

    def test_edit_act_wout_music_and_continue(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        data = self.get_full_post()
        data['finish_to_advanced'] = "Proceed to Advanced"
        del data['finish_basics']
        data['confirm_no_music'] = 1
        response = self.client.post(url, data, follow=True)
        assert_alert_exists(
            response, 'success', 'Success', default_act_tech_basic_submit)
        self.assertContains(response,
                            "Advanced Technical Information (Optional)")
        self.assertContains(response,
                            "Start with the stage blacked out")

    def test_get_advanced(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.confirm_no_music = True
        context.act.tech.mic_choice = mic_options[2][0]
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.feel_of_act = "feel"
        context.act.tech.starting_position = "Onstage"
        context.act.tech.primary_color = "Red"
        context.act.performer.pronouns = "Me/Myself"
        context.act.tech.duration = timedelta(minutes=2)
        context.act.tech.introduction_text = "Yo this is an intro"
        context.act.tech.start_blackout = True
        context.act.tech.end_blackout = True
        context.act.tech.special_lighting_cue = "so special!"
        context.act.tech.save()
        context.act.performer.save()
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.get(url)
        self.assertContains(response,
                            'Advanced Technical Information (Optional)')
        assert_option_state(
            response,
            str(context.rehearsal.id),
            date_format(context.rehearsal.starttime, "TIME_FORMAT"),
            True)
        self.assertContains(response,
                            'name="%d-booking_id"' % context.sched_event.pk)
        self.assertContains(
            response,
            '<input type="checkbox" name="start_blackout" ' +
            'id="id_start_blackout" checked />',
            html=True)
        self.assertContains(
            response,
            '<input type="checkbox" name="end_blackout" ' +
            'id="id_end_blackout" checked />',
            html=True)
        self.assertContains(response, "so special!")
        assert_option_state(response,
                            mic_options[2][0],
                            mic_options[2][1],
                            True)
        self.assert_radio_state(response,
                                'pronouns_0',
                                'id_pronouns_0_3',
                                '',
                                checked=True,
                                required=True)
        self.assertContains(
            response,
            '<input type="text" name="pronouns_1" id="id_pronouns_0" ' +
            'value="Me/Myself">',
            html=True)

    def test_post_good_advanced(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.confirm_no_music = True
        context.act.tech.mic_choice = mic_options[2]
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.feel_of_act = "feel"
        context.act.tech.starting_position = "Onstage"
        context.act.tech.primary_color = "Red"
        context.act.tech.duration = timedelta(minutes=2)
        context.act.tech.introduction_text = "Yo this is an intro"
        context.act.tech.save()
        data = {
            'mic_choice': mic_options[2],
            'follow_spot_color': 'red',
            'background_color': 'blue',
            'wash_color': 'purple',
            'special_lighting_cue': 'when I drop my pants, make it pink',
            'start_blackout': True,
            'end_blackout': True,
        }
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('home', urlconf='gbe.urls'))
        assert_alert_exists(
            response, 'success', 'Success', default_act_tech_advanced_submit)

    def test_post_bad_advanced(self):
        context = ActTechInfoContext(schedule_rehearsal=True)
        context.act.tech.confirm_no_music = True
        context.act.tech.mic_choice = mic_options[2]
        context.act.tech.prop_setup = "[u'I have props I will need set " + \
            "before my number']"
        context.act.tech.feel_of_act = "feel"
        context.act.tech.starting_position = "Onstage"
        context.act.tech.primary_color = "Red"
        context.act.tech.duration = timedelta(minutes=2)
        context.act.tech.introduction_text = "Yo this is an intro"
        context.act.tech.save()
        data = {
            'mic_choice': "These are bad",
            'follow_spot_color': 'red',
            'background_color': 'blue',
            'wash_color': 'purple',
            'special_lighting_cue': 'when I drop my pants, make it pink',
            'start_blackout': True,
            'end_blackout': True,
        }
        url = reverse(self.view_name,
                      urlconf='gbe.urls',
                      args=[context.act.pk])
        login_as(context.performer.contact, self)
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Select a valid choice.')
        self.assertContains(response,
                            "Advanced Technical Information (Optional)")
