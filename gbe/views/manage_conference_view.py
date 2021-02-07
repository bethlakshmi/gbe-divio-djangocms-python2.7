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
from gbe.forms import ConferenceStartChangeForm
from gbe.models import (
    Conference,
    ConferenceDay,
    UserMessage
)
from gbe.functions import validate_profile
from gbetext import (
    default_update_profile_msg,
    change_day_note,
)
from django.core.exceptions import PermissionDenied
from django.http import Http404


class ManageConferenceView(View):
    title = "Manage Conference"
    button = "Change Dates"
    header = "Change Conference Start Day"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ManageConferenceView, self).dispatch(*args, **kwargs)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_profile(request, require=False)
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
            forms += [(first_day,
                       ConferenceStartChangeForm(instance=first_day))]

        return render(request, 'gbe/manage_conference.tmpl',
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
        form = ConferenceStartChangeForm(request.POST)
        if not form.is_valid():
            # return error
            return render(
                request,
                'gbe/manage_conference.tmpl',
                {'forms': [form],
                 'intro': intro_message,
                 'title': self.title,
                 'button': self.button,
                 'header': self.header})
        conf_change = form.cleaned_data['day'] - day.day
        for each_day in day.conference.conferenceday_set.all():
            each_day.day = each_day.day + conf_change
            each_day.save()
        messages.success(
            request,
            "Moved Conference %s by %d days, change %d conference days" % (
                day.conference.conference_slug,
                conf_change.days,
                day.conference.conferenceday_set.count()))
        return render(request, 'gbe/manage_conference.tmpl',
                      {'forms': [],
                       'intro': intro_message,
                       'title': self.title,
                       'button': self.button,
                       'header': self.header})
