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
    StaffArea,
)
from gbe.functions import (
    get_latest_conference,
    get_conference_by_slug,
    conference_list,
    validate_perms,
)
from scheduler.idd import get_occurrences
from gbe.scheduling.forms import SelectEventForm
from gbetext import (
    calendar_for_event,
    calendar_type,
)
import string


class ManageEventsView(View):
    template = 'gbe/scheduling/manage_event.tmpl'
    conference = None

    def groundwork(self, request, args, kwargs):
        validate_perms(request, ('Scheduling Mavens', 'Admins'))
        self.conference = None
        conference_set = conference_list()

        if "conference_slug" in kwargs:
            self.conference = get_conference_by_slug(
                kwargs['conference_slug'])
        else:
            self.conference = get_latest_conference()
            
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
            'view_title': "Events",
        }
        if 'new' in list(request.GET.keys()):
            context['success_occurrences'] = eval(request.GET['new'])
        if 'alt_id' in list(request.GET.keys()):
            context['alt_id'] = int(request.GET['alt_id'])
        return context

    def build_occurrence_display(self, occurrences):
        display_list = []
        for occurrence in occurrences:
            if calendar_for_event[occurrence.event_style] == "Conference":
                copy_link = None
            else:
                copy_link = reverse('copy_event_schedule',
                                    urlconf='gbe.scheduling.urls',
                                    args=[occurrence.id])
            display_item = {
                'id': occurrence.id,
                'start':  occurrence.start_time,
                'title': occurrence.title,
                'location': occurrence.location,
                'duration': occurrence.length.total_seconds(
                    ) / timedelta(hours=1).total_seconds(),
                'type': occurrence.event_style,
                'current_volunteer': occurrence.role_count("Volunteer"),
                'current_acts': occurrence.role_count("Performer"),
                'max_volunteer': occurrence.max_volunteer,
                'max_commitments': occurrence.max_commitments,
                'approval_needed': occurrence.approval_needed,
                'staff_areas': [],
                'detail_link': reverse(
                    'detail_view',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.pk]),
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
                display_item['parent_title'] = parent.title
                display_item['parent_link'] = reverse(
                    'edit_event',
                    urlconf='gbe.scheduling.urls',
                    args=[self.conference.conference_slug, parent.pk])
                if self.conference.status == "completed":
                    display_item['parent_link'] = reverse(
                        'detail_view',
                        urlconf='gbe.scheduling.urls',
                        args=[parent.pk])
            for area in StaffArea.objects.filter(slug__in=occurrence.labels,
                                                 conference=self.conference):
                display_item['staff_areas'] += [area]
            display_list += [display_item]
        return display_list

    def get_filtered_occurrences(self, request, select_form):
        occurrences = []
        label_set = [[self.conference.conference_slug]]
        event_styles = []
        day = None

        if select_form.is_valid():
            if len(select_form.cleaned_data['calendar_type']) > 0:
                cal_types = []
                for cal_type in select_form.cleaned_data['calendar_type']:
                    cal_types += [calendar_type[int(cal_type)]]
                label_set += [cal_types]
                select_form.fields['calendar_type'].label = (
                    '<b>%s</b>' % ', '.join(cal_types))
            if len(select_form.cleaned_data['event_style']) > 0:
                for event_style in select_form.cleaned_data['event_style']:
                    event_styles += [event_style]
                select_form.fields['event_style'].label = (
                    '<b>%s</b>' % ', '.join(event_styles))
            if len(select_form.cleaned_data['staff_area']) > 0:
                staff_areas = []
                staff_area_labels = []

                for staff_area in select_form.cleaned_data['staff_area']:
                    staff_areas += [staff_area.slug]
                    staff_area_labels += [staff_area.title]
                label_set += [staff_areas]
                select_form.fields['staff_area'].label = (
                    '<b>%s</b>' % ', '.join(staff_area_labels))
            if len(select_form.cleaned_data['day']) > 0:
                days = []
                for day_id in select_form.cleaned_data['day']:
                    day = ConferenceDay.objects.get(pk=day_id)
                    response = get_occurrences(label_sets=label_set,
                                               event_styles=event_styles,
                                               day=day.day)
                    days += [str(day)]
                    occurrences += response.occurrences
                select_form.fields['day'].label = '<b>%s</b>' % ', '.join(days)

        if day is None:
            response = get_occurrences(label_sets=label_set,
                                       event_styles=event_styles)
            occurrences += response.occurrences
        return self.build_occurrence_display(occurrences)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)

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
