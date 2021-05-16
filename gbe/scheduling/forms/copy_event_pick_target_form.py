from django.forms import (
    CheckboxSelectMultiple,
    ChoiceField,
    ModelChoiceField,
    MultipleChoiceField,
    Form,
    RadioSelect,
)
from gbe.models import (
    ConferenceDay,
    Class,
    GenericEvent,
    Room,
    Show,
    StaffArea,
)
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT
)
from gbe_forms_text import (
    copy_mode_labels,
    copy_mode_choices,
    copy_mode_solo_choices,
    copy_errors,
)
from scheduler.idd import get_occurrences
from django.db.models.fields import BLANK_CHOICE_DASH


class TargetDay(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s - %s" % (
            obj.conference.conference_slug,
            obj.day.strftime(GBE_DATE_FORMAT))


class CopyEventPickDayForm(Form):
    '''
    Form for selecting the type of event to create
    '''
    required_css_class = 'required'
    error_css_class = 'error'

    copy_to_day = TargetDay(
        queryset=ConferenceDay.objects.exclude(
            conference__status="completed").order_by('day'),
        required=False
        )
    room = ModelChoiceField(
        queryset=Room.objects.filter(
            conferences__status__in=("ongoing", "upcoming")
            ).order_by('name').distinct(),
        required=True,
        label=copy_mode_labels['room'])

    def clean(self):
        cleaned_data = super(CopyEventPickDayForm, self).clean()
        copy_to_day = cleaned_data.get("copy_to_day")
        room = cleaned_data.get("room")
        if copy_to_day and not room.conferences.filter(
                pk=copy_to_day.conference.pk).exists():
            msg = copy_errors['room_conf_mismatch']
            self.add_error('room', msg)
        return cleaned_data


class CopyEventPickModeForm(CopyEventPickDayForm):
    '''
    Form for selecting the type of event to create
    '''
    copy_mode = ChoiceField(choices=copy_mode_choices,
                            label=copy_mode_labels['copy_mode'],
                            widget=RadioSelect)

    target_event = ChoiceField(choices=[],
                               required=False)

    def __init__(self, *args, **kwargs):
        event_type = None
        choices = []
        events = None
        if 'event_type' in kwargs:
            event_type = kwargs.pop('event_type')
        super(CopyEventPickModeForm, self).__init__(*args, **kwargs)
        if event_type == "Show":
            events = Show.objects.exclude(
                e_conference__status="completed")
        elif event_type == "Class":
            events = Class.objects.exclude(
                e_conference__status="completed")
        elif event_type != "Staff":
            events = GenericEvent.objects.exclude(
                e_conference__status="completed").filter(type=event_type)
        if events:
            response = get_occurrences(
                foreign_event_ids=events.values_list('eventitem_id',
                                                     flat=True))
            if response.occurrences:
                for occurrence in response.occurrences:
                    choices += [(occurrence.pk, "%s - %s" % (
                        str(occurrence),
                        occurrence.start_time.strftime(GBE_DATETIME_FORMAT)))]
        else:
            areas = StaffArea.objects.exclude(
                conference__status="completed")
            for area in areas:
                choices += [(area.pk, area.title)]
        self.fields['target_event'].choices = BLANK_CHOICE_DASH + choices
        self.fields['target_event'].label = copy_mode_labels['room']

    def clean(self):
        cleaned_data = super(CopyEventPickModeForm, self).clean()
        copy_mode = cleaned_data.get("copy_mode")
        target_event = cleaned_data.get("target_event")
        copy_to_day = cleaned_data.get("copy_to_day")
        if copy_mode:
            if copy_mode == copy_mode_choices[0][0] and not target_event:
                msg = copy_errors['no_target']
                self.add_error('target_event', msg)
            if copy_mode == copy_mode_choices[1][0] and not copy_to_day:
                msg = copy_errors['no_day']
                self.add_error('copy_to_day', msg)
        return cleaned_data


class CopyEventSoloPickModeForm(CopyEventPickModeForm):
    '''
    Form for selecting the type of event to create
    '''
    copy_mode = MultipleChoiceField(choices=copy_mode_solo_choices,
                                    label=copy_mode_labels['copy_mode_solo'],
                                    required=True,
                                    widget=CheckboxSelectMultiple)
    area = ModelChoiceField(
        queryset=StaffArea.objects.exclude(conference__status="completed"),
        required=False)

    def __init__(self, *args, **kwargs):
        event_type = None
        choices = []
        events = None
        super(CopyEventSoloPickModeForm, self).__init__(*args, **kwargs)
        shows = Show.objects.exclude(e_conference__status="completed")
        specials = GenericEvent.objects.exclude(
                e_conference__status="completed").filter(type="Special")
        response = get_occurrences(
            foreign_event_ids=list(
                shows.values_list('eventitem_id',flat=True)) +
            list(specials.values_list('eventitem_id',flat=True)))
        if response.occurrences:
            for occurrence in response.occurrences:
                choices += [(occurrence.pk, "%s - %s" % (
                    str(occurrence),
                    occurrence.start_time.strftime(GBE_DATETIME_FORMAT)))]
        self.fields['target_event'].choices = BLANK_CHOICE_DASH + choices
        self.fields['target_event'].label = copy_mode_labels['solo_room']
        self.fields['target_event'].label = copy_mode_labels['solo_room']

    def clean(self):
        cleaned_data = super(CopyEventPickModeForm, self).clean()
        copy_mode = cleaned_data.get("copy_mode")
        target_event = cleaned_data.get("target_event")
        copy_to_day = cleaned_data.get("copy_to_day")
        area = cleaned_data.get("area")
        if copy_mode_solo_choices[0][0] in copy_mode and not target_event:
            msg = copy_errors['no_target']
            self.add_error('target_event', msg)
        if copy_mode_solo_choices[1][0] in copy_mode and not area:
            msg = copy_errors['no_area']
            self.add_error('area', msg)
        if copy_mode_solo_choices[2][0] not in copy_mode and (
                copy_mode_solo_choices[0][0] not in copy_mode):
            msg = copy_errors['no_delta']
            self.add_error('copy_mode', msg)
        if copy_mode_solo_choices[2][0] in copy_mode and not copy_to_day:
            msg = copy_errors['no_day']
            self.add_error('copy_to_day', msg)
        return cleaned_data
