from django.views.generic import View
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.formats import date_format
from datetime import timedelta
from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
    URL_DATE,
)
from gbe.models import (
    ConferenceDay,
    Event,
    GenericEvent,
    StaffArea,
)
from gbe.functions import (
    get_current_conference,
    get_conference_by_slug,
    conference_list,
    validate_perms,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.forms import (
    HiddenSelectEventForm,
    SelectEventForm,
)
from gbetext import calendar_type as calendar_type_options


class ManageEventsView(View):
    template = 'gbe/scheduling/manage_event.tmpl'
    conference = None

    def groundwork(self, request, args, kwargs):
        validate_perms(request, ('Scheduling Mavens', 'Admins'))
        context = {}
        self.conference = None
        conference_set = conference_list().order_by('-conference_slug')

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_current_conference()

        day_list = []
        for day in self.conference.conferenceday_set.all():
            day_list += [(day.pk, day.day.strftime(GBE_DATE_FORMAT))]
        select_form = SelectEventForm(request.GET,
                                      prefix=self.conference.conference_slug)
        select_form.fields['day'].choices = day_list
        select_form.fields['staff_area'].queryset = StaffArea.objects.filter(
            conference=self.conference
        ).order_by("slug")
        context = {
            'conference': self.conference,
            'conference_slugs': [
                conf.conference_slug for conf in conference_set],
            'selection_form': select_form,
            'other_forms': [],
        }
        if 'new' in list(request.GET.keys()):
            context['success_occurrences'] = eval(request.GET['new'])
        if 'alt_id' in list(request.GET.keys()):
            context['alt_id'] = int(request.GET['alt_id'])
        for conf in conference_set:
            if self.conference != conf:
                hidden_form = HiddenSelectEventForm(
                    request.GET,
                    prefix=conf.conference_slug)
                conf_day_list = []
                for day in conf.conferenceday_set.all():
                    conf_day_list += [(day.pk,
                                       day.day.strftime(GBE_DATE_FORMAT))]
                hidden_form.fields['day'].choices = conf_day_list
                context['other_forms'] += [hidden_form]
        return context

    def build_occurrence_display(self, occurrences):
        display_list = []
        events = Event.objects.filter(e_conference=self.conference)
        for occurrence in occurrences:
            event_type = events.filter(
                    eventitem_id=occurrence.eventitem.eventitem_id
                    ).get_subclass().event_type
            if event_type == "Class":
                copy_link = None
            else:
                copy_link = reverse('copy_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[occurrence.id])
            display_item = {
                'id': occurrence.id,
                'start':  occurrence.start_time,
                'title': occurrence.eventitem.event.e_title,
                'location': occurrence.location,
                'duration': occurrence.eventitem.event.duration.total_seconds(
                    ) / timedelta(hours=1).total_seconds(),
                'type': event_type,
                'current_volunteer': occurrence.role_count("Volunteer"),
                'current_acts': occurrence.role_count("Performer"),
                'max_volunteer': occurrence.max_volunteer,
                'max_commitments': occurrence.max_commitments,
                'approval_needed': occurrence.approval_needed,
                'staff_areas': [],
                'detail_link': reverse(
                    'detail_view',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.eventitem.event.eventitem_id]),
                'delete_link': reverse('delete_occurrence',
                                       urlconf='gbe.scheduling.urls',
                                       args=[occurrence.id]),
                'copy_link': copy_link}
            if self.conference.status != "completed":
                display_item['edit_link'] = reverse(
                    'edit_event',
                    urlconf='gbe.scheduling.urls',
                    args=[self.conference.conference_slug,
                          occurrence.pk])
            if occurrence.parent is not None:
                parent = occurrence.parent
                display_item['parent_title'] = parent.eventitem.event.e_title
                display_item['parent_link'] = reverse(
                    'edit_event',
                    urlconf='gbe.scheduling.urls',
                    args=[self.conference.conference_slug, parent.pk])
                if self.conference.status == "completed":
                    display_item['parent_link'] = reverse(
                        'detail_view',
                        urlconf='gbe.scheduling.urls',
                        args=[parent.eventitem.event.eventitem_id])
            for area in StaffArea.objects.filter(slug__in=occurrence.labels,
                                                 conference=self.conference):
                display_item['staff_areas'] += [area]
            display_list += [display_item]
        return display_list

    def get_filtered_occurrences(self, request, select_form):
        occurrences = []
        label_set = [[self.conference.conference_slug]]

        if len(select_form.cleaned_data['calendar_type']) > 0:
            cal_types = []
            for cal_type in select_form.cleaned_data['calendar_type']:
                cal_types += [calendar_type_options[int(cal_type)]]
            label_set += [cal_types]
        if len(select_form.cleaned_data['staff_area']) > 0:
            staff_areas = []
            for staff_area in select_form.cleaned_data['staff_area']:
                staff_areas += [staff_area.slug]
            label_set += [staff_areas]
        if len(select_form.cleaned_data['day']) > 0:
            for day_id in select_form.cleaned_data['day']:
                day = ConferenceDay.objects.get(pk=day_id)
                response = get_occurrences(label_sets=label_set,
                                           day=day.day)
                occurrences += response.occurrences
        else:
            response = get_occurrences(
                label_sets=label_set)
            occurrences += response.occurrences

        return self.build_occurrence_display(occurrences)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)

        if context['selection_form'].is_valid() and (
                len(context['selection_form'].cleaned_data['day']) > 0 or len(
                    context['selection_form'].cleaned_data[
                        'calendar_type']) > 0 or len(
                    context['selection_form'].cleaned_data['staff_area']) > 0):
            context['occurrences'] = self.get_filtered_occurrences(
                request,
                context['selection_form'])
            context['columns'] = [
                'Title',
                'Parent',
                'Area',
                'Location',
                'Date/Time',
                'Duration',
                'Type',
                'Current #',
                'Max #',
                'Action']
            context['order'] = 4
        return render(request, self.template, context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageEventsView, self).dispatch(*args, **kwargs)
