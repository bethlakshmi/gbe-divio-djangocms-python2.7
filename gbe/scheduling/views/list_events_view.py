from django.views.generic import View
from django.shortcuts import (
    render,
)
from django.http import Http404
from django.urls import reverse
from gbe.models import (
    Bio,
    Class,
    StaffArea,
    UserMessage,
)
from gbe.scheduling.forms import DisplayEventForm
from gbe.forms import InvolvedProfileForm
from gbe.functions import (
    get_latest_conference,
    get_conference_by_slug,
    conference_slugs,
)
from gbe.scheduling.views.functions import build_icon_links
from scheduler.idd import (
    get_bookings,
    get_schedule,
    get_eval_info,
    get_occurrences,
)
from scheduler.data_transfer import Person
from gbe_forms_text import (
    list_text,
    list_titles,
)
from gbetext import (
    calendar_for_event,
    class_styles,
    login_please,
    role_options,
    paired_alert_msg,
    pending_note,
)


class ListEventsView(View):
    template = 'gbe/scheduling/event_display_list.tmpl'
    conference = None
    event_type = "All"

    def groundwork(self, request, args, kwargs):
        context = {}
        form = None

        if "event_type" in kwargs:
            self.event_type = kwargs['event_type']
            if self.event_type.lower() not in list_titles:
                raise Http404

        if "conference" in self.request.GET:
            self.conference = get_conference_by_slug(
                self.request.GET.get('conference', None))
        else:
            self.conference = get_latest_conference()

        if self.event_type == "Volunteer":
            form = DisplayEventForm(request.GET)
            form.fields['staff_area'].queryset = StaffArea.objects.filter(
                conference=self.conference).order_by("slug")
        if not self.conference:
            raise Http404

        pending_instructions = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PENDING_INSTRUCTIONS",
            defaults={
                'summary': "Pending Instructions (in modal, approval needed)",
                'description': pending_note})
        login_please_msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="LOGIN_REQUIRED",
            defaults={
                'summary': "Login or setup account message",
                'description': login_please})
        header_text = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="%s_INSTRUCTIONS" % self.event_type.upper(),
                defaults={
                    'summary': "Text on top of event list pages",
                    'description': list_text.get(self.event_type.lower(), "")})
        paired_alert = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PAIRED_EVENT_MSG",
            defaults={
                'summary': "Shown in any Paired Event Popup",
                'description': paired_alert_msg})
        context = {
            'conf_slug': self.conference.conference_slug,
            'conference_slugs': conference_slugs(),
            'filter_form': form,
            'title': list_titles.get(self.event_type.lower(), ""),
            'view_header_text': header_text[0].description,
            'pending_note': pending_instructions[0].description,
            'login_please': login_please_msg[0].description,
            'paired_event_alert': paired_alert[0].description

        }

        return context

    def get_styles(self):
        styles = [self.event_type]

        if self.event_type == "All":
            styles = []
            for style, calendar in calendar_for_event.items():
                if calendar is not None:
                    styles += [style]

        elif self.event_type == 'Class' or self.event_type == 'class':
            styles = class_styles

        return styles

    def get_classes(self, occurrences):
        class_types = []
        classes = []
        scheduled_events = []
        if self.event_type in ["All", 'Class', 'class']:
            class_types = class_styles
        elif self.event_type in class_styles:
            class_types = [self.event_type]

        if len(class_types) > 0:
            booked_classes = occurrences.exclude(
                connected_id__isnull=True).values_list('connected_id',
                                                       flat=True)
            classes = Class.objects.filter(
                b_conference=self.conference,
                type__in=class_types,
                accepted='3').exclude(
                pk__in=booked_classes)
        return classes

    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        eval_occurrences = []
        all_roles = []
        personal_schedule_items = []
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            person = Person(
                users=[request.user],
                public_id=request.user.profile.pk,
                public_class=request.user.profile.__class__.__name__)
            for n, m in role_options:
                all_roles += [m]
            personal_schedule_items = get_schedule(
                request.user,
                labels=[self.conference.conference_slug],
                roles=all_roles,
                ).schedule_items

            eval_response = get_eval_info(person=person)
            if len(eval_response.questions) > 0:
                eval_occurrences = eval_response.occurrences
            else:
                eval_occurrences = None
            if not request.user.profile.participation_ready:
                context['complete_profile_form'] = InvolvedProfileForm(
                    instance=request.user.profile,
                    initial={'first_name': request.user.first_name,
                             'last_name': request.user.last_name})

        label_set = [[self.conference.conference_slug]]
        if context['filter_form'] is not None and (
                context['filter_form'].is_valid()) and (
                len(context['filter_form'].cleaned_data['staff_area']) > 0):
            staff_areas = []
            for staff_area in context['filter_form'].cleaned_data[
                    'staff_area']:
                staff_areas += [staff_area.slug]
            label_set += [staff_areas]
        response = get_occurrences(
            event_styles=self.get_styles(),
            label_sets=label_set)

        scheduled_events = []
        for occurrence in response.occurrences:
            presenters = []
            (favorite_link,
             volunteer_link,
             evaluate,
             highlight,
             vol_disable_msg) = build_icon_links(
                occurrence,
                eval_occurrences,
                calendar_for_event[occurrence.event_style],
                (self.conference.status == "completed"),
                personal_schedule_items)
            people_response = get_bookings([occurrence.pk], roles=[
                "Teacher",
                "Moderator",
                "Panelist"])
            for person in people_response.people:
                if person.public_class != "Profile":
                    presenter = Bio.objects.get(pk=person.public_id)
                    if presenter not in presenters:
                        presenters += [presenter]
            bid = None
            if (occurrence.connected_class is not None) and (
                    occurrence.connected_class == "Class"):
                bid = Class.objects.get(pk=occurrence.connected_id)

            scheduled_events += [{
                'occurrence': occurrence,
                'favorite_link': favorite_link,
                'volunteer_link': volunteer_link,
                'highlight': highlight,
                'evaluate': evaluate,
                'vol_disable_msg': vol_disable_msg,
                'approval_needed': occurrence.approval_needed,
                'presenters': sorted(presenters,
                                     key=lambda person: person.name.lower()),
                'bid': bid,
                'detail': reverse('detail_view',
                                  urlconf='gbe.scheduling.urls',
                                  args=[occurrence.pk])}]

        unscheduled_classes = self.get_classes(response.occurrences)
        context['events'] = scheduled_events
        context['unscheduled'] = unscheduled_classes
        return render(request, self.template, context)

    def dispatch(self, *args, **kwargs):
        return super(ListEventsView, self).dispatch(*args, **kwargs)
