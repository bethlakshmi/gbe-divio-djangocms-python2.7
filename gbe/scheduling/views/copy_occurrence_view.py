from gbe.scheduling.views import CopyCollectionsView
from django.http import (
    Http404,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.urls import reverse
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
    StaffArea,
    UserMessage,
)
from gbe.functions import validate_perms
from gbe_forms_text import (
    copy_mode_solo_choices,
)
from gbe.scheduling.forms import CopyEventSoloPickModeForm
from gbetext import (
    calendar_for_event,
    copy_solo_intro,
)


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
        if calendar_for_event[self.occurrence.event_style] == "Conference":
            return HttpResponseForbidden("Class copy is not yet available")
        self.start_day = self.occurrence.starttime.date()
        response = get_occurrences(parent_event_id=self.occurrence_id)
        self.children = response.occurrences
        show_general_status(request, response, self.__class__.__name__)

    def make_context(self, request, post=None):
        context = {
            'first_title': "Copying - %s: %s" % (
                self.occurrence.title,
                self.occurrence.starttime.strftime(self.copy_date_format)),
            'event_type': self.occurrence.event_style,
            'room': self.occurrence.location.as_subtype}
        return super(CopyOccurrenceView, self).make_context(request,
                                                            context,
                                                            post)

    def setup_solo(self, context, post):
        area = None
        if StaffArea.objects.exclude(
                conference__status="completed").filter(
                slug__in=self.occurrence.labels).exists():
            area = StaffArea.objects.exclude(
                conference__status="completed").filter(
                slug__in=self.occurrence.labels).first()
        context['copy_solo_mode'] = CopyEventSoloPickModeForm(
            post,
            initial={'room': context['room'], 'area': area})
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="COPY_SOLO_INTRO",
            defaults={
                'summary': "Copying event with no children instructions",
                'description': copy_solo_intro})
        context['introduction'] = user_message[0].description
        return context

    def get_copy_target(self, context):
        response = get_occurrence(
            context['copy_mode'].cleaned_data['target_event'])
        conference = Conference.objects.filter(
            conference_slug__in=response.occurrence.labels)[0]
        second_title = "Destination is %s: %s" % (
            conference.conference_slug,
            response.occurrence.title)
        delta = response.occurrence.starttime.date() - self.start_day
        return second_title, delta, conference

    def copy_event(self,
                   occurrence,
                   delta,
                   conference,
                   room,
                   labels,
                   parent_event_id=None,
                   set_room=False):
        new_event_room = room
        if (not set_room) and \
                occurrence.location.as_subtype.conferences.filter(
                pk=conference.pk).exists():
            new_event_room = occurrence.location

        response = create_occurrence(
            occurrence.title,
            occurrence.duration,
            occurrence.event_style,
            occurrence.starttime + delta,
            max_volunteer=occurrence.max_volunteer,
            max_commitments=occurrence.max_commitments,
            locations=[new_event_room],
            description=occurrence.duration,
            parent_event_id=parent_event_id,
            labels=labels,
            approval=occurrence.approval_needed,
            slug=occurrence.slug
        )
        return response

    def copy_root(self, request, delta, conference, room):
        new_occurrence = None
        labels = [conference.conference_slug,
                  calendar_for_event[self.occurrence.event_style]]
        for area in StaffArea.objects.filter(
                conference=conference,
                slug__in=self.occurrence.labels):
            labels += [area.slug]
        response = self.copy_event(
            self.occurrence,
            delta,
            conference,
            room,
            labels,
            set_room=True)
        show_scheduling_occurrence_status(
            request,
            response,
            self.__class__.__name__)
        if response.occurrence:
            new_occurrence = response.occurrence
        return new_occurrence

    def copy_solo(self, request, context):
        delta = None
        parent_event_id = None
        copy_mode = context['copy_solo_mode'].cleaned_data['copy_mode']
        if copy_mode_solo_choices[2][0] in copy_mode:
            target_day = context['copy_solo_mode'].cleaned_data['copy_to_day']
            conference = target_day.conference
            delta = target_day.day - self.start_day
        if copy_mode_solo_choices[0][0] in copy_mode:
            parent_event_id = context['copy_solo_mode'].cleaned_data[
                'target_event']
            resp = get_occurrence(context['copy_solo_mode'].cleaned_data[
                'target_event'])
            if delta is None:
                delta = resp.occurrence.starttime.date() - self.start_day
                conference = Conference.objects.filter(
                    conference_slug__in=resp.occurrence.labels)[0]

        labels = [conference.conference_slug,
                  calendar_for_event[self.occurrence.event_style]]
        if copy_mode_solo_choices[1][0] in copy_mode:
            labels += [context['copy_solo_mode'].cleaned_data['area'].slug]

        response = self.copy_event(
            self.occurrence,
            delta,
            conference,
            context['copy_solo_mode'].cleaned_data['room'],
            labels,
            parent_event_id=parent_event_id,
            set_room=True)

        show_scheduling_occurrence_status(
            request,
            response,
            self.__class__.__name__)
        if response.occurrence:
            target_day = ConferenceDay.objects.filter(
                day=response.occurrence.starttime.date(),
                conference=conference
                ).first()
            return HttpResponseRedirect(
                "%s?%s-day=%d&filter=Filter&new=%s" % (
                    reverse('manage_event_list',
                            urlconf='gbe.scheduling.urls',
                            args=[conference.conference_slug]),
                    conference.conference_slug,
                    target_day.pk,
                    str([response.occurrence.pk]),))

    def get_child_copy_settings(self, form):
        response = get_occurrence(
            form.cleaned_data['target_event'])
        conference = Conference.objects.filter(
            conference_slug__in=response.occurrence.labels)[0]
        target_day = ConferenceDay.objects.filter(
            day=response.occurrence.starttime.date(),
            conference=conference
            ).first()
        delta = response.occurrence.starttime.date(
            ) - self.start_day
        new_root = response.occurrence
        return (new_root, target_day, delta, conference)
