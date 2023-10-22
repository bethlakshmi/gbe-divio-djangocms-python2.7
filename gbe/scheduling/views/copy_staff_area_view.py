from collections import Counter
from gbe.scheduling.views import CopyCollectionsView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from scheduler.idd import (
    create_occurrence,
    get_occurrences,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import StaffArea
from gbe.functions import validate_perms
from datetime import (
    datetime,
    timedelta
)
from settings import GBE_DATETIME_FORMAT
from django.utils.text import slugify
from django.contrib import messages
from gbe.models import UserMessage
from gbetext import no_conf_day_msg
from django.urls import reverse
from gbe.scheduling.forms import CopyEventPickDayForm


class CopyStaffAreaView(CopyCollectionsView):
    permissions = ('Scheduling Mavens',)
    area = None

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        self.area = get_object_or_404(StaffArea,
                                      id=int(kwargs['staff_id']))
        if self.area.conference.conferenceday_set.count() > 0:
            self.start_day = self.area.conference.conferenceday_set.order_by(
                "day").first().day
        else:
            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_CONF_DAYS",
                defaults={
                    'summary': "No Conference Days in Conference",
                    'description': no_conf_day_msg})
            messages.error(
                request,
                user_message[0].description)
            return HttpResponseRedirect(reverse(
                'manage_event_list',
                urlconf='gbe.scheduling.urls',
                args=[self.area.conference.conference_slug]))

        response = get_occurrences(labels=[
            self.area.slug,
            self.area.conference.conference_slug])
        self.children = response.occurrences
        show_general_status(request, response, self.__class__.__name__)

    def make_context(self, request, post=None):
        context = {
            'first_title': "Copying - %s" % self.area.title,
            'event_type': "Staff",
            'room': self.area.default_location}
        return super(CopyStaffAreaView, self).make_context(request,
                                                           context,
                                                           post)

    def setup_solo(self, context, post):
        context['pick_day'] = CopyEventPickDayForm(
            post,
            initial={'room': context['room']})
        context['pick_day'].fields['copy_to_day'].empty_label = None
        context['pick_day'].fields['copy_to_day'].required = True
        return context

    def get_copy_target(self, context):
        area = get_object_or_404(
            StaffArea,
            id=context['copy_mode'].cleaned_data['target_event'])
        second_title = "Destination is %s: %s" % (
            area.conference.conference_slug,
            area.title)
        if area.conference == self.area.conference:
            delta = timedelta()
        else:
            delta = area.conference.conferenceday_set.order_by("day").first(
                ).day - self.start_day
        return second_title, delta, area.conference

    def copy_root(self, request, delta, conference, room):
        new_area_room = room
        new_title = self.area.title
        new_slug = self.area.slug
        if conference == self.area.conference or StaffArea.objects.filter(
                conference=conference, title=self.area.title):
            now = datetime.now().strftime(GBE_DATETIME_FORMAT)
            new_title = "%s - New - %s" % (
                self.area.title,
                now)
            new_slug = "%s_new_%s" % (
                self.area.slug,
                slugify(now))
        if (not self.area.default_location) or (
                self.area.default_location.conferences.filter(
                    pk=conference.pk).exists()):
            new_area_room = self.area.default_location
        new_area = StaffArea(
            conference=conference,
            title=new_title,
            slug=new_slug,
            description=self.area.description,
            default_location=new_area_room,
            default_volunteers=self.area.default_volunteers
        )
        new_area.save()
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="STAFF_AREA_COPIED",
            defaults={
                'summary': "Staff Area Copy Success",
                'description': "A new Staff Area was created."})
        messages.success(
            request,
            "%s<br>Staff Area: %s" % (
                user_message[0].description,
                new_area.title))
        return [new_area]

    def copy_solo(self, request, context):
        target_day = context['pick_day'].cleaned_data['copy_to_day']
        delta = target_day.day - self.start_day
        new_root = self.copy_root(
            request,
            delta,
            target_day.conference,
            context['pick_day'].cleaned_data['room'])

        if len(new_root) > 0:
            slug = target_day.conference.conference_slug
            return HttpResponseRedirect(
                "%s?%s-day=%d&filter=Filter&new=%s" % (
                        reverse('manage_event_list',
                                urlconf='gbe.scheduling.urls',
                                args=[slug]),
                        slug,
                        target_day.pk,
                        str([new_root[0].pk]),))

    def copy_event(self,
                   occurrence,
                   delta,
                   conference,
                   room,
                   labels,
                   root=None):
        new_event_room = room
        event_labels = labels.copy()
        peer_id = None
        peer_response = None
        if root:
            event_labels += [self.area.slug]
        if occurrence.location.as_subtype.conferences.filter(
                pk=conference.pk).exists():
            new_event_room = occurrence.location

        if occurrence.peer is not None:
            # peers share labels - same conf, both volunteer positions
            # if the parents are the same, use the parent, if not, leave null
            peer_room = room
            peer_labels = labels
            if occurrence.peer.location.as_subtype.conferences.filter(
                    pk=conference.pk).exists():
                peer_room = occurrence.peer.location
            if Counter(occurrence.peer.labels) == Counter(occurrence.labels):
                peer_labels = event_labels
            peer_response = create_occurrence(
                occurrence.peer.title,
                occurrence.peer.duration,
                occurrence.peer.event_style,
                occurrence.peer.starttime + delta,
                max_volunteer=occurrence.peer.max_volunteer,
                max_commitments=occurrence.peer.max_commitments,
                locations=[peer_room],
                description=occurrence.peer.description,
                labels=peer_labels,
                approval=occurrence.peer.approval_needed,
                slug=occurrence.peer.slug)
            peer_id = peer_response.occurrence.pk

        response = create_occurrence(
            occurrence.title,
            occurrence.duration,
            occurrence.event_style,
            occurrence.starttime + delta,
            max_volunteer=occurrence.max_volunteer,
            locations=[new_event_room],
            description=occurrence.duration,
            labels=event_labels,
            approval=occurrence.approval_needed,
            slug=occurrence.slug,
            peer_id=peer_id
        )
        return response, peer_response

    def get_child_copy_settings(self, form):
        new_root = StaffArea.objects.get(
            id=form.cleaned_data['target_event'])
        target_day = new_root.conference.conferenceday_set.order_by(
            "day").first()
        delta = target_day.day - self.start_day
        conference = new_root.conference
        return (new_root, target_day, delta, conference)
