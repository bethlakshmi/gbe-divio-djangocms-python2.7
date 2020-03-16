from django.conf import settings
from django.db.models import (
    BooleanField,
    CharField,
    DurationField,
    FileField,
    Model,
    TextField,
)
from gbetext import (
    mic_options,
)
from gbe_forms_text import *


class TechInfo(Model):
    # Basic Info
    track_title = CharField(max_length=128, blank=True)
    track_artist = CharField(max_length=123, blank=True)
    duration = DurationField(null=True)
    feel_of_act = TextField(blank=True)
    introduction_text = TextField(max_length=1000, blank=True)
    read_exact = BooleanField(default=False)
    prop_setup = TextField(blank=True)
    crew_instruct = TextField(blank=True)
    pronouns = CharField(max_length=128, blank=True)
    primary_color = CharField(max_length=128, blank=True)
    secondary_color = CharField(max_length=128, blank=True)
    follow_spot = BooleanField(default=False)
    starting_position = CharField(max_length=128, blank=True)
    track = FileField(upload_to='uploads/audio', blank=True)
    confirm_no_music = BooleanField(default=False)

    # Advanced Info
    mic_choice = CharField(max_length=200,
                           choices=mic_options,
                           default=mic_options[0][0])
    background_color = CharField(max_length=128, blank=True)
    wash_color = CharField(max_length=128, blank=True)
    follow_spot_color = CharField(max_length=128, blank=True)
    special_lighting_cue = TextField(blank=True)
    start_blackout = BooleanField(default=False)
    end_blackout = BooleanField(default=False)

    def clone(self):
        ti = TechInfo()
        ti.save()
        return ti

    @property
    def is_complete(self):
        audio_complete = (self.confirm_no_music or
                          (self.track_title and
                           self.track_artist and
                           self.track))
        return bool(self.duration and
                    self.prop_setup and
                    self.starting_position and
                    self.primary_color and
                    self.feel_of_act and
                    self.pronouns and
                    audio_complete and
                    self.introduction_text)

    def __unicode__(self):
        try:
            return "Techinfo: " + self.act.b_title
        except:
            return "Techinfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'tech info'
        app_label = "gbe"
