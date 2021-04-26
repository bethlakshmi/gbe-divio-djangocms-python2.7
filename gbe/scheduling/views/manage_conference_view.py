from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from gbe_logging import log_func
from gbe.scheduling.forms import ConferenceStartChangeForm
from gbe.models import (
    Conference,
    ConferenceDay,
    UserMessage
)
from gbe.functions import validate_perms
from gbetext import (
    change_day_note,
    missing_day_form_note,
)
from django.core.exceptions import PermissionDenied
from django.http import Http404
from scheduler.idd import (
    get_occurrences,
    update_occurrence)
from gbe.scheduling.views.functions import show_general_status
from settings import URL_DATE


class ManageConferenceView(View):
    title = "Manage Conference"
    button = "Change Dates"
    header = "Change Conference Start Day"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageConferenceView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, ("Scheduling Mavens", ))
        if not self.profile.user_object.is_superuser:
            raise PermissionDenied
        message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="CHANGE_CONF_DAY_INTRO",
            defaults={
                'summary': "Change Conference Day Instructions",
                'description': change_day_note})
        return message[0].description

    @never_cache
    @log_func
    def get(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        forms = []
        for conference in Conference.objects.filter(
                status__in=('upcoming', 'ongoing')):
            first_day = ConferenceDay.objects.filter(
                conference=conference).order_by('day').first()
            if first_day is not None:
                forms += [(first_day,
                           ConferenceStartChangeForm(instance=first_day,
                                                     prefix=first_day.pk))]

        return render(request, 'gbe/scheduling/manage_conference.tmpl',
                      {'forms': forms,
                       'intro': intro_message,
                       'title': self.title,
                       'button': self.button,
                       'header': self.header})

    @never_cache
    @log_func
    def post(self, request, *args, **kwargs):
        intro_message = self.groundwork(request, args, kwargs)
        if "day_id" in kwargs:
            day = get_object_or_404(ConferenceDay, pk=kwargs.get("day_id"))
        else:
            raise Http404
        all_valid = True
        forms = []
        the_form = None
        for conference in Conference.objects.filter(
                status__in=('upcoming', 'ongoing')):
            first_day = ConferenceDay.objects.filter(
                conference=conference).order_by('day').first()
            if first_day is not None:
                form = ConferenceStartChangeForm(request.POST,
                                                 instance=first_day,
                                                 prefix=first_day.pk)
                if first_day == day:
                    form.fields['day'].required = True
                    the_form = form
                all_valid = all_valid and form.is_valid()
                forms += [(first_day, form)]

        if the_form is None:
            messages.error(request, UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="NO_CONF_DAY_FORM",
                defaults={
                   'summary': "Conference Day Form Not Loaded",
                   'description': missing_day_form_note})[0].description)
            all_valid = False

        if not all_valid:
            return render(
                request,
                'gbe/scheduling/manage_conference.tmpl',
                {'forms': forms,
                 'intro': intro_message,
                 'title': self.title,
                 'button': self.button,
                 'header': self.header})
        conf_change = the_form.cleaned_data['day'] - day.day

        # update each conference day so form selection offers right choices
        for each_day in day.conference.conferenceday_set.all():
            each_day.day = each_day.day + conf_change
            each_day.save()
        messages.success(
            request,
            "Moved Conference %s by %d days, change %d conference days" % (
                day.conference.conference_slug,
                conf_change.days,
                day.conference.conferenceday_set.count()))

        # update all scheduled events
        event_count = 0
        response = get_occurrences(
            labels=[day.conference.conference_slug])
        for occurrence in response.occurrences:
            occ_response = update_occurrence(
                occurrence.pk,
                start_time=occurrence.starttime + conf_change)
            show_general_status(request, occ_response, self.__class__.__name__)
            if occ_response and occ_response.occurrence:
                event_count = event_count + 1
        messages.success(
            request,
            "Moved %d scheduled events by %d days" % (
                event_count,
                conf_change.days))
        general_calendar_links = ""
        class_calendar_links = ""
        volunteer_calendar_links = ""
        for each_day in day.conference.conferenceday_set.filter(
                open_to_public=True).order_by('day'):
            general_calendar_links = "%s<li>%s - %s?day=%s" % (
                general_calendar_links,
                each_day.day.strftime("%A"),
                reverse("calendar",
                        urlconf='gbe.scheduling.urls',
                        args=['General']),
                each_day.day.strftime(URL_DATE))
            class_calendar_links = "%s<li>%s - %s?day=%s" % (
                class_calendar_links,
                each_day.day.strftime("%A"),
                reverse("calendar",
                        urlconf='gbe.scheduling.urls',
                        args=['Conference']),
                each_day.day.strftime(URL_DATE))
            volunteer_calendar_links = "%s<li>%s - %s?day=%s" % (
                volunteer_calendar_links,
                each_day.day.strftime("%A"),
                reverse("calendar",
                        urlconf='gbe.scheduling.urls',
                        args=['Volunteer']),
                each_day.day.strftime(URL_DATE))
        messages.warning(
            request,
            ("REMINDER: Don't forget to change the calendar links: <ul>" +
             "<li>Special Events</li><ul>%s</ul><li>Conference Events</li>" +
             "<ul>%s</ul><li>Volunteer Events</li><ul>%s</ul></ul>") % (
                general_calendar_links,
                class_calendar_links,
                volunteer_calendar_links))

        return HttpResponseRedirect(
            ("%s?%s-calendar_type=0&%s-calendar_type=1&%s-calendar_type=2" +
             "&filter=Filter") % (
             reverse('manage_event_list', urlconf='gbe.scheduling.urls'),
             day.conference.conference_slug,
             day.conference.conference_slug,
             day.conference.conference_slug))
