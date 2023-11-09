from django.utils.safestring import mark_safe
from django.forms import (
    CharField,
    CheckboxSelectMultiple,
    ChoiceField,
    ModelForm,
    MultipleChoiceField,
    RadioSelect,
    Textarea,
)
from django_addanother.widgets import AddAnotherEditSelectedWidgetWrapper
from dal import autocomplete
from django.urls import reverse_lazy
from gbe.forms import BasicBidForm
from gbe.models import (
    Class,
    UserMessage,
)
from gbe_forms_text import (
    available_time_conflict,
    unavailable_time_conflict,
    classbid_help_texts,
    classbid_labels,
    class_schedule_options,
    difficulty_default_text,
)
from gbetext import difficulty_options
from gbe.functions import jsonify


class ClassBidDraftForm(ModelForm, BasicBidForm):
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
    difficulty = ChoiceField(
        widget=RadioSelect,
        choices=difficulty_options,
        required=False)

    class Meta:
        model = Class
        fields = ['b_title',
                  'teacher_bio',
                  'first_name',
                  'last_name',
                  'phone',
                  'b_description',
                  'maximum_enrollment',
                  'type',
                  'difficulty',
                  'fee',
                  'length_minutes',
                  'history',
                  'schedule_constraints',
                  'avoided_constraints',
                  'space_needs']
        help_texts = classbid_help_texts
        labels = classbid_labels
        widgets = {
            'teacher_bio': AddAnotherEditSelectedWidgetWrapper(
                autocomplete.ModelSelect2(url=reverse_lazy(
                    'limited-persona-autocomplete',
                    urlconf='gbe.urls')),
                reverse_lazy('persona-add', urlconf='gbe.urls'),
                reverse_lazy('persona-update',
                             urlconf='gbe.urls',
                             args=['__fk__'])),
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
        dynamic_difficulty_options = []
        for choice in difficulty_options:
            label_desc, created = UserMessage.objects.get_or_create(
                view="MakeClassView",
                code="%s_DIFFICULTY" % choice[0].upper(),
                defaults={
                    'summary': "%s Difficulty Description" % choice[0],
                    'description': difficulty_default_text[choice[0]]})
            dynamic_difficulty_options += [(
                choice[0],
                mark_safe("<b>%s:</b> %s" % (choice[1],
                                             label_desc.description)))]
        self.fields['difficulty'].choices = dynamic_difficulty_options

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
