from django.core.management.base import BaseCommand
from django.conf import settings
import optparse
import tarfile
import os
import shutil
from gbe.models import (
    Show,
    Act,
)
from gbe.functions import get_conference_by_slug


def make_safe_filename(unsafe_string):
    '''This is probably wheel reinvention, but I haven't found the wheel
    If we keep it, it should be improved and turned into a utility function
    '''
    return unsafe_string.replace(' ', '_').replace('/', '_')


def tarfile_name(show_name, conf_slug):
    return make_safe_filename("%s_%s.tar.gz" % (conf_slug, show_name))


def add_acts_for_show(show_name, conf_slug, tar):
    '''
    for acts in show, add track for act to tar
    '''
    conference = get_conference_by_slug(conf_slug)
    acts = Show.objects.get(e_conference__conference_slug=conf_slug,
                            e_title=show_name).get_acts()
    workdir = make_safe_filename("%s_%s" % (conf_slug, show_name))
    os.mkdir(workdir)

    for act in acts:
        if act and act.tech.track:
            fname = os.path.basename(act.tech.track.path)
            workname = os.path.join(workdir, fname)
            shutil.copyfile(fname, workname)
            tar.add(workname)
    tar.close()
    shutil.rmtree(workdir)


class Command(BaseCommand):
    help = 'Synchronize the per-show audio download'
    audio_directory = os.path.join(settings.MEDIA_ROOT, 'uploads', 'audio')

    downloads_directory = os.path.join(audio_directory,
                                       'downloads')

    def add_arguments(self, parser):
        parser.add_argument(
            "--unsync",
            action="store_true",
            dest="unsync",
            default=False,
            help='move a given set of songs to the stale_downloads directory')
        parser.add_argument(
            "--unsync_all",
            action="store_true",
            dest="unsync_all",
            default=False,
            help='move a all sets songs to the stale_downloads directory')
        parser.add_argument("--show", type=str, dest="show_name")
        parser.add_argument("--conference", type=str, dest="conf_slug"),

    def create_downloads_directory(self):
        path_parts = ['uploads', 'audio', 'downloads', 'stale_downloads']
        path = settings.MEDIA_ROOT
        for part in path_parts:
            path = os.path.join(path, part)
            if not os.path.exists(path):
                os.mkdir(path)

    def is_synced(self, show_name, conf_slug):
        '''
        return True if the download archive for this show exists
        and is current
        '''
        filename = tarfile_name(show_name, conf_slug)

        filepath = os.path.join(self.downloads_directory, filename)
        return os.path.exists(filepath)

    def tarfile_for(self, show_name, conf_slug):
        '''
        return a handle to a suitable tarfile object for this show
        '''
        filename = tarfile_name(show_name, conf_slug)
        path = os.path.join(self.downloads_directory, filename)
        return tarfile.open(path, "w:gz")

    def sync(self, show_name, conf_slug):
        curr_dir = os.path.realpath(".")
        os.chdir(self.audio_directory)
        if self.is_synced(show_name, conf_slug):
            os.chdir(curr_dir)
            return
        tar = self.tarfile_for(show_name, conf_slug)
        add_acts_for_show(show_name, conf_slug, tar)
        os.chdir(curr_dir)

    def unsync(self, show_name, conf_slug):
        if not self.is_synced(show_name, conf_slug):
            return
        filename = tarfile_name(show_name, conf_slug)
        oldpath = os.path.join(self.downloads_directory, filename)
        newpath = os.path.join(self.downloads_directory,
                               "stale_downloads",
                               filename)
        os.rename(oldpath, newpath)

    def unsync_all(self):
        workdir = self.downloads_directory
        destdir = os.path.join(workdir, "stale_downloads")
        for file in os.listdir(workdir):
            if os.path.isfile(os.path.join(workdir, file)):
                os.rename(os.path.join(workdir, file),
                          os.path.join(destdir, file))

    def handle(self, *args, **options):
        self.create_downloads_directory()
        show_name = options['show_name']
        conf_slug = options['conf_slug']
        if options['unsync_all']:
            self.unsync_all()
        elif options['unsync']:
            self.unsync(show_name, conf_slug)
        else:
            self.sync(show_name, conf_slug)
