from django.test import TestCase
from django.test import Client
from django.core.management import call_command
from django.conf import settings
from tests.contexts import ActTechInfoContext
import os


class TestSyncAudioDownloads(TestCase):

    def setUp(self):
        self.client = Client()
        self.context = ActTechInfoContext(room_name="Theater")

    def test_unsync(self):
        call_command("sync_audio_downloads",
                     unsync=True,
                     show_name=self.context.show.e_title,
                     conf_slug=self.context.conference.conference_slug)
        filename = os.path.join(
            settings.MEDIA_ROOT,
            'uploads/audio/downloads',
            "%s_%s.tar.gz" % (self.context.conference.conference_slug,
                              self.context.show.e_title.replace(' ', '_')))
        self.assertFalse(os.path.isfile(filename))
        filename = os.path.join(
            settings.MEDIA_ROOT,
            'uploads/audio/downloads/stale_downloads',
            "%s_%s.tar.gz" % (self.context.conference.conference_slug,
                              self.context.show.e_title.replace(' ', '_')))
        self.assertFalse(os.path.isfile(filename))

    def test_unsync_after_sync(self):
        call_command('sync_audio_downloads',
                     show_name=self.context.show.e_title,
                     conf_slug=self.context.conference.conference_slug)
        call_command("sync_audio_downloads",
                     unsync=True,
                     show_name=self.context.show.e_title,
                     conf_slug=self.context.conference.conference_slug)
        filename = os.path.join(
            settings.MEDIA_ROOT,
            'uploads/audio/downloads/stale_downloads',
            "%s_%s.tar.gz" % (self.context.conference.conference_slug,
                              self.context.show.e_title.replace(' ', '_')))
        self.assertTrue(os.path.isfile(filename))
