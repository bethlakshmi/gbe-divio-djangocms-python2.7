from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.files import File
from tests.factories.gbe_factories import ProfileFactory
from tests.contexts import ActTechInfoContext
from tests.functions.gbe_functions import (
    grant_privilege,
    login_as,
)
from django.conf import settings
from io import BytesIO
import tarfile
import os
import shutil


class TestDownloadTracksForShow(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = ProfileFactory()
        grant_privilege(self.profile, "Tech Crew")
        self.context = ActTechInfoContext(room_name="Theater")        

    def test_download_tracks_for_show(self):
        login_as(self.profile, self)
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.show.pk]))
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                self.context.conference.conference_slug,
                self.context.show.e_title.replace(' ', '_'))))

    def test_download_and_mkdir(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            'uploads/audio/downloads/stale_downloads')
        shutil.rmtree(path)
        login_as(self.profile, self)
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.show.pk]))
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                self.context.conference.conference_slug,
                self.context.show.e_title.replace(' ', '_'))))

    def test_download_twice(self):
        path = os.path.join(settings.MEDIA_ROOT,
                            'uploads/audio/downloads/stale_downloads')
        shutil.rmtree(path)
        login_as(self.profile, self)
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.show.pk]))
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.show.pk]))
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                self.context.conference.conference_slug,
                self.context.show.e_title.replace(' ', '_'))))

'''
--- Refactor all of this someday.  This is a useful test, but the way
    this system is doing file handling makes a reasonable test really 
    hard -----
    def test_download_tracks_for_show_w_audio(self):
        filename = open("tests/gbe/gbe_pagebanner.png", 'r')
        track = File(filename)
        self.context.audio.track = track
        self.context.audio.save()
        login_as(self.profile, self)
        response = self.client.get(reverse('download_tracks_for_show',
                                           urlconf='gbe.reporting.urls',
                                           args=[self.context.show.pk]))
        self.assertEquals(
            response.get('Content-Disposition'),
            str('attachment; filename="%s_%s.tar.gz"' % (
                self.context.conference.conference_slug,
                self.context.show.e_title.replace(' ', '_'))))
        f = BytesIO(response.content)
        results = tarfile.open(mode="r:gz", fileobj=f)
        self.assertTrue("%s_%s/gbe_pagebanner" % (
            self.context.conference.conference_slug,
            self.context.show.e_title.replace(' ', '_')
            ) in results.getnames()[0])
        results.close()
        f.close()
'''
