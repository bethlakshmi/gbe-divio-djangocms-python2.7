from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ModelForm,
    MultipleChoiceField,
    Textarea,
)
from django_addanother.widgets import AddAnotherEditSelectedWidgetWrapper
from dal import autocomplete
from django.urls import reverse_lazy
from gbe.models import Class
from gbe_forms_text import (
    available_time_conflict,
    unavailable_time_conflict,
    classbid_help_texts,
    classbid_labels,
    class_schedule_options,
    participant_form_help_texts,
    participant_labels,
)
from gbe.functions import jsonify


class ClassBidDraftForm(ModelForm):
    use_required_attribute = False
    required_css_class = 'required'
    error_css_class = 'error'
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        required=False,
        label=classbid_labels['schedule_constraints']
    )
    avoided_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['avoided_constraints'],
        required=False)
    b_description = CharField(
        required=True,
        widget=Textarea(attrs={'id': 'user-tiny-mce'}),
        label=classbid_labels['b_description'])
    phone = CharField(required=True,
                      help_text=participant_form_help_texts['phone'])
    first_name = CharField(
        required=True,
        label=participant_labels['legal_first_name'])
    last_name = CharField(
        required=True,
        label=participant_labels['legal_last_name'],
        help_text=participant_form_help_texts['legal_name'])

    class Meta:
        model = Class
        fields = ['b_title',
                  'teacher',
                  'first_name',
                  'last_name',
                  'phone',
                  'b_description',
                  'maximum_enrollment',
                  'type',
                  'fee',
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'avoided_constraints',
                  'space_needs']
        help_texts = classbid_help_texts
        labels = classbid_labels
        widgets = {
            'teacher': AddAnotherEditSelectedWidgetWrapper(
                autocomplete.ModelSelect2(url='limited-persona-autocomplete'),
                reverse_lazy('persona-add', urlconf='gbe.urls', args=[0]),
                reverse_lazy('persona-update',
                             urlconf='gbe.urls',
                             args=['__fk__', 0])),
            }

    def __init__(self, *args, **kwargs):
        super(ClassBidDraftForm, self).__init__(*args, **kwargs)
        if self.instance:
            obj_data = self.instance.__dict__
            if obj_data['schedule_constraints']:
                self.initial['schedule_constraints'] = jsonify(
                    obj_data['schedule_constraints'])
            if obj_data['avoided_constraints']:
                self.initial['avoided_constraints'] = jsonify(
                    obj_data['avoided_constraints'])

    def clean(self):
        cleaned_data = super(ClassBidDraftForm, self).clean()
        conflict_windows = []
        if ('schedule_constraints' in self.cleaned_data) and (
                'avoided_constraints' in self.cleaned_data):
            conflict_windows = set(
                self.cleaned_data['schedule_constraints']).intersection(
                self.cleaned_data['avoided_constraints'])
        if len(conflict_windows) > 0:
            windows = ", ".join(
                class_schedule_options[int(w)][1] for w in conflict_windows)
            self._errors['schedule_constraints'] = \
                available_time_conflict % windows
            self._errors['avoided_constraints'] = \
                unavailable_time_conflict
        if 'b_title' in cleaned_data:
            cleaned_data['b_title'] = cleaned_data['b_title'].strip('\'\"')
        return cleaned_data


class ClassBidForm(ClassBidDraftForm):
    schedule_constraints = MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        choices=class_schedule_options,
        label=classbid_labels['schedule_constraints'])
    b_description = CharField(
        required=True,
        widget=Textarea(attrs={'id': 'user-tiny-mce'}),
        label=classbid_labels['b_description'])
