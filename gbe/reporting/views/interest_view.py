from gbe_utils.mixins import (
    ConferenceListView,
    RoleRequiredMixin,
)
from django.urls import reverse
from scheduler.idd import get_occurrences
from gbe.models import (
    Bio,
    Class,
    UserMessage,
)
from gbetext import interested_report_explain_msg


class InterestView(RoleRequiredMixin, ConferenceListView):
    model = Class
    template_name = 'gbe/report/interest.tmpl'
    view_permissions = 'any'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = get_occurrences(
            labels=[self.conference.conference_slug, "Conference"])
        context['columns'] = ['Class',
                              'Teacher',
                              'Location',
                              'Max attendees',
                              'Style',
                              'Interested',
                              'Action']

        display_list = []
        for occurrence in response.occurrences:
            class_event = Class.objects.get(pk=occurrence.connected_id)
            teachers = []
            interested = []
            for person in occurrence.people:
                if person.role == "Interested":
                    interested += [person]
                elif person.role in ("Teacher", "Moderator"):
                    teachers += [Bio.objects.get(pk=person.public_id)]

            display_item = {
                'id': occurrence.id,
                'title': occurrence.title,
                'location': occurrence.location,
                'teachers': teachers,
                'interested': interested,
                'type': occurrence.event_style,
                'maximum_enrollment': class_event.maximum_enrollment,
                'detail_link': reverse(
                    'detail_view',
                    urlconf='gbe.scheduling.urls',
                    args=[occurrence.pk])}
            display_list += [display_item]

        context['about'] = UserMessage.objects.get_or_create(
            view="InterestView",
            code="ABOUT_INTERESTED",
            defaults={
               'summary': "About Interested Attendee Report",
               'description': interested_report_explain_msg})[0].description
        context['classes'] = display_list
        return context
