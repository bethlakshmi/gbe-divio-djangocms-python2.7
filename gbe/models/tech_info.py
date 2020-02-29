from django.conf import settings
from django.db.models import (
    BooleanField,
    CharField,
    DurationField,
    FileField,
    ForeignKey,
    Model,
    OneToOneField,
    PositiveIntegerField,
    TextField,
)

from gbetext import (
    cyc_color_options,
    offon_options,
    follow_spot_options,
    stage_lighting_options,
)
from gbe_forms_text import *


###################
# Technical info #
# includes       #
# AudioInfo      #
# StageInfo      #
# LightingInfo   #
# CueInfo        #
###################


class AudioInfo(Model):
    '''
    Information about the audio required for a particular Act
    '''
    track_title = CharField(max_length=128, blank=True)
    track_artist = CharField(max_length=123, blank=True)
    track = FileField(upload_to='uploads/audio', blank=True)
    track_duration = DurationField(blank=True)
    need_mic = BooleanField(default=False, blank=True)
    own_mic = BooleanField(default=False, blank=True)
    notes = TextField(blank=True)
    confirm_no_music = BooleanField(default=False)

    @property
    def dump_data(self):
        return [self.track_title.encode('utf-8').strip(),
                self.track_artist.encode('utf-8').strip(),
                self.track,
                self.track_duration,
                self.need_mic,
                self.own_mic,
                self.notes.encode('utf-8').strip(),
                self.confirm_no_music
                ]

    def clone(self):
        ai = AudioInfo(track_title=self.track_title,
                       track_artist=self.track_artist,
                       track=self.track,
                       track_duration=self.track_duration,
                       need_mic=self.need_mic,
                       own_mic=self.own_mic,
                       notes=self.notes,
                       confirm_no_music=self.confirm_no_music)
        ai.save()
        return ai

    @property
    def is_complete(self):
        return bool(self.confirm_no_music or
                    (self.track_title and
                     self.track_artist and
                     self.track_duration
                     ))

    def __unicode__(self):
        try:
            return "AudioInfo: " + self.techinfo.act.b_title
        except:
            return "AudioInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'audio info'
        app_label = "gbe"


class LightingInfo (Model):
    '''
    Information about the basic (not related to cues) lighting
    needs of a particular Act
    '''
    notes = TextField(blank=True)
    costume = TextField(blank=True)
    specific_needs = TextField(blank=True)

    def clone(self):
        li = LightingInfo(notes=self.notes,
                          costume=self.costume)
        li.save()
        return li

    @property
    def dump_data(self):
        return [self.notes.encode('utf-8').strip(),
                self.costume.encode('utf-8').strip()]

    @property
    def is_complete(self):
        return True

    @property
    def incomplete_warnings(self):
        if self.is_complete:
            return {}
        else:
            return {"lighting": lightinginfo_incomplete_warning}

    def __unicode__(self):
        try:
            return "LightingInfo: " + self.techinfo.act.b_title
        except:
            return "LightingInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'lighting info'
        app_label = "gbe"


class StageInfo(Model):
    '''
    Information about the stage requirements for a particular Act
    confirm field should be offered if the user tries to save with all
    values false and no notes
    '''
    act_duration = DurationField(blank=True)
    intro_text = TextField(blank=True)
    confirm = BooleanField(default=False)
    set_props = BooleanField(default=False)
    cue_props = BooleanField(default=False)
    clear_props = BooleanField(default=False)
    notes = TextField(blank=True)

    def clone(self):
        si = StageInfo(act_duration=self.act_duration,
                       intro_text=self.intro_text,
                       confirm=self.confirm,
                       set_props=self.set_props,
                       cue_props=self.cue_props,
                       clear_props=self.clear_props,
                       notes=self.notes)
        si.save()
        return si

    @property
    def dump_data(self):
        return [self.act_duration,
                self.intro_text.encode('utf-8').strip(),
                self.confirm,
                self.set_props,
                self.cue_props,
                self.clear_props,
                self.notes.encode('utf-8').strip(),
                ]

    @property
    def is_complete(self):
        return bool(self.set_props or
                    self.clear_props or
                    self.cue_props or self.confirm)

    @property
    def incomplete_warnings(self):
        if self.is_complete:
            return {}
        else:
            return {'stage': stageinfo_incomplete_warning}

    def __unicode__(self):
        try:
            return "StageInfo: " + self.techinfo.act.b_title
        except:
            return "StageInfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'stage info'
        app_label = "gbe"


class TechInfo(Model):
    '''
    Gathers up technical info about an act in a show.
    BB - doing 2 additional cues for now for an easy add to existing DB
      2015  - may want to consider a many to many field for 1+ cues
    '''
    audio = OneToOneField(AudioInfo, blank=True)
    lighting = OneToOneField(LightingInfo, blank=True)
    stage = OneToOneField(StageInfo, blank=True)

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

    def clone(self):
        ti = TechInfo()
        ti.audio = self.audio.clone()
        ti.lighting = self.lighting.clone()
        ti.stage = self.stage.clone()
        ti.save()
        for ci in CueInfo.objects.filter(techinfo=self):
            ci.clone(self)
        return ti

    @property
    def is_complete(self):
        return bool(self.duration and
                    self.prop_setup and
                    self.starting_position and
                    self.primary_color and
                    self.feel_of_act and
                    self.pronouns and
                    self.introduction_text)

    def get_incomplete_warnings(self):
        warnings = {}
        warnings.update(self.lighting.incomplete_warnings)
        warnings.update(self.audio.incomplete_warnings)
        warnings.update(self.stage.incomplete_warnings)
        return warnings

    def __unicode__(self):
        try:
            return "Techinfo: " + self.act.b_title
        except:
            return "Techinfo: (deleted act)"

    class Meta:
        verbose_name_plural = 'tech info'
        app_label = "gbe"


class CueInfo(Model):
    '''
    Information about the lighting needs of a particular Act as they
    relate to one or more cues within the Act.  Each item is the change
    that occurs after a cue
    '''
    cue_sequence = PositiveIntegerField(default=0)
    cue_off_of = TextField()

    follow_spot = CharField(max_length=25,
                            choices=follow_spot_options,
                            default=follow_spot_options[0])

    center_spot = CharField(max_length=20,
                            choices=offon_options, default="OFF")

    backlight = CharField(max_length=20,
                          choices=offon_options, default="OFF")

    cyc_color = CharField(max_length=25,
                          choices=cyc_color_options,
                          default=cyc_color_options[0])

    wash = CharField(max_length=25,
                     choices=stage_lighting_options,
                     default=stage_lighting_options[0])
    sound_note = TextField(blank=True)
    techinfo = ForeignKey(TechInfo)

    def clone(self, techinfo):
        CueInfo(cue_sequence=self.cue_sequence,
                cue_off_of=self.cue_off_of,
                follow_spot=self.follow_spot,
                center_spot=self.center_spot,
                backlight=self.backlight,
                cyc_color=self.cyc_color,
                wash=self.wash,
                sound_note=self.sound_note,
                techinfo=techinfo).save()

    @property
    def is_complete(self):
        return bool(self.cue_off_of and self.cue_sequence and self.tech_info)

    def __unicode__(self):
        try:
            return "%s - cue %s" % (self.techinfo.act.title,
                                    str(self.cue_sequence))
        except:
            return "Cue: (deleted act) - %s" % str(self.cue_sequence)

    class Meta:
        verbose_name_plural = "cue info"
        app_label = "gbe"
