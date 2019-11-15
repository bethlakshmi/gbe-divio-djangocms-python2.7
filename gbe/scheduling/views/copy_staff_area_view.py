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
from django.core.urlresolvers import reverse


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
        if conference == self.area.conference:
            now = datetime.now().strftime(GBE_DATETIME_FORMAT)
            new_title = "%s - New - %s" % (
                self.area.title,
                now)
            new_slug = "%s_new_%s" % (
                self.area.slug,
                slugify(now))
        if self.area.default_location.conferences.filter(
                pk=conference.pk).exists():
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
        return new_area

    def copy_event(self, occurrence, delta, conference, room, root=None):
        new_event_room = room
        gbe_event_copy = occurrence.as_subtype
        gbe_event_copy.pk = None
        gbe_event_copy.event_id = None
        gbe_event_copy.eventitem_ptr_id = None
        gbe_event_copy.eventitem_id = None
        gbe_event_copy.e_conference = conference
        gbe_event_copy.save()
        labels = [conference.conference_slug,
                  gbe_event_copy.calendar_type]
        if root:
            labels += [root.slug]
        if occurrence.location.as_subtype.conferences.filter(
                pk=conference.pk).exists():
            new_event_room = occurrence.location

        response = create_occurrence(
            gbe_event_copy.eventitem_id,
            occurrence.starttime + delta,
            max_volunteer=occurrence.max_volunteer,
            locations=[new_event_room],
            labels=labels
        )
        return response

    def get_child_copy_settings(self, form):
        new_root = StaffArea.objects.get(
            id=form.cleaned_data['target_event'])
        target_day = new_root.conference.conferenceday_set.order_by(
            "day").first()
        delta = target_day.day - self.start_day
        conference = new_root.conference
        return (new_root, target_day, delta, conference)
