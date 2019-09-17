from django import forms
from gbe.models import Show
from scheduler.models import Event


class ActScheduleForm(forms.Form):
    '''
    Presents an act for scheduling as one line on a multi-line form.
    '''
    performer = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    title = forms.CharField(
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    show = forms.ModelChoiceField(queryset=Event.objects.all())
    order = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ActScheduleForm, self).__init__(*args, **kwargs)
        if 'initial' in kwargs:
            initial = kwargs.pop('initial')
            conf_shows = Show.objects.filter(
                e_conference=initial['show'].eventitem.get_conference())
            self.fields['show'].queryset = Event.objects.filter(
                eventitem__in=conf_shows)
