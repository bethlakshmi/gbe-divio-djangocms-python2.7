from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from gbe.models import (
    Profile,
    UserMessage,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import (
    conference_slugs,
    get_latest_conference,
    get_conference_by_slug,
    validate_perms,
)
from scheduler.idd import get_schedule
from gbe.ticketing_idd_interface import get_checklist_items
from gbetext import (
    unsigned_forms_message,
    welcome_message
)


class WelcomeLetterView(View):
    profiles = None

    def groundwork(self, request, args, kwargs):
        viewer_profile = validate_perms(request, 'any', require=True)

        if request.GET and request.GET.get('conf_slug'):
            self.conference = get_conference_by_slug(request.GET['conf_slug'])
        else:
            self.conference = get_latest_conference()

        if "profile_id" in kwargs:
            self.profiles = [get_object_or_404(
                Profile,
                pk=kwargs['profile_id'])]
        else:
            self.profiles = Profile.objects.filter(
                user_object__is_active=True).select_related()

    @never_cache
    def get(self, request, *args, **kwargs):
        self.groundwork(request, args, kwargs)
        schedules = []
        welcome_msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="INTRO_MESSAGE",
            defaults={
                'summary': "Welcome Message",
                'description': welcome_message})
        unsigned_forms_msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="UNSIGNED_FORMS_MESSAGE",
            defaults={
                'summary': "Unsigned Form Alert Message",
                'description': unsigned_forms_message})

        for person in self.profiles:
            response = get_schedule(
                person.user_object,
                labels=[self.conference.conference_slug])
            if len(response.schedule_items) > 0 or len(self.profiles) == 1:
                ticket_items, role_items, unsigned_forms = get_checklist_items(
                    person.user_object,
                    self.conference,
                    response.schedule_items)
                schedules += [{'person': person,
                               'bookings': response.schedule_items,
                               'ticket_items': ticket_items,
                               'role_items': role_items,
                               'unsigned_forms': unsigned_forms}]

        sorted_sched = sorted(
            schedules,
            key=lambda schedule: schedule['person'].get_badge_name())
        return render(
            request,
            'gbe/report/printable_schedules.tmpl',
            {'schedules': sorted_sched,
             'conference_slugs': conference_slugs(),
             'conference': self.conference,
             'welcome_message': welcome_msg[0].description,
             'unsigned_forms_message': unsigned_forms_msg[0].description})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(WelcomeLetterView, self).dispatch(*args, **kwargs)
