from gbe.scheduling.views import CopyCollectionsView
from django.http import Http404
from scheduler.idd import (
    create_occurrence,
    get_occurrence,
    get_occurrences,
)
from gbe.scheduling.views.functions import (
    show_general_status,
    show_scheduling_occurrence_status,
)
from gbe.models import (
    Conference,
    ConferenceDay,
)
from gbe.functions import validate_perms


class CopyOccurrenceView(CopyCollectionsView):
    permissions = ('Scheduling Mavens',)
    occurrence = None

    def groundwork(self, request, args, kwargs):
        self.occurrence_id = int(kwargs['occurrence_id'])
        self.profile = validate_perms(request, self.permissions)
        response = get_occurrence(self.occurrence_id)
        show_general_status(request, response, self.__class__.__name__)
        if not response.occurrence:
            raise Http404
        self.occurrence = response.occurrence
        self.start_day = self.occurrence.starttime.date()
        response = get_occurrences(parent_event_id=self.occurrence_id)
        self.children = response.occurrences
        show_general_status(request, response, self.__class__.__name__)

    def make_context(self, request, post=None):
        context = {
            'first_title': "Copying - %s: %s" % (
                self.occurrence.eventitem.event.e_title,
                self.occurrence.starttime.strftime(self.copy_date_format)),
            'event_type': self.occurrence.as_subtype.event_type}
        return super(CopyOccurrenceView, self).make_context(request,
                                                            context,
                                                            post)

    def get_copy_target(self, context):
        response = get_occurrence(
            context['copy_mode'].cleaned_data['target_event'])
        event = response.occurrence.eventitem.event
        second_title = "Destination is %s: %s" % (
            event.e_conference.conference_slug,
            event.e_title)
        delta = response.occurrence.starttime.date() - self.start_day
        return second_title, delta

    def copy_event(self, occurrence, delta, conference, root=None):
        parent_event_id = None
        if root:
            parent_event_id = root.pk
        gbe_event_copy = occurrence.as_subtype
        gbe_event_copy.pk = None
        gbe_event_copy.event_id = None
        gbe_event_copy.eventitem_ptr_id = None
        gbe_event_copy.eventitem_id = None
        gbe_event_copy.e_conference = conference
        gbe_event_copy.save()
        labels = [conference.conference_slug]
        for label in occurrence.labels:
            if not Conference.objects.filter(conference_slug=label).exists():
                labels += [label]
        response = create_occurrence(
            gbe_event_copy.eventitem_id,
            occurrence.starttime + delta,
            max_volunteer=occurrence.max_volunteer,
            locations=[occurrence.location],
            parent_event_id=parent_event_id,
            labels=labels
        )
        return response

    def copy_root(self, request, delta, conference):
        new_occurrence = None
        response = self.copy_event(
            self.occurrence,
            delta,
            conference)
        show_scheduling_occurrence_status(
            request,
            response,
            self.__class__.__name__)
        if response.occurrence:
            new_occurrence = response.occurrence
        return new_occurrence

    def get_child_copy_settings(self, form):
        response = get_occurrence(
            form.cleaned_data['target_event'])
        target_day = ConferenceDay.objects.filter(
            day=response.occurrence.starttime.date(),
            conference=response.occurrence.eventitem.event.e_conference
        ).first()
        delta = response.occurrence.starttime.date(
            ) - self.start_day
        conference = response.occurrence.eventitem.event.e_conference
        new_root = response.occurrence
        return (new_root, target_day, delta, conference)
