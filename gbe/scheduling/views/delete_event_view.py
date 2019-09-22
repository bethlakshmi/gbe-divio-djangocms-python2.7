from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from scheduler.idd import (
    get_occurrence,
    get_occurrences,
    delete_occurrence,
)
from gbe.scheduling.views.functions import show_general_status
from gbe.models import UserMessage
from gbe.functions import validate_perms
from settings import GBE_DATETIME_FORMAT


class DeleteEventView(View):
    permissions = ('Scheduling Mavens',)

    def groundwork(self, request, args, kwargs):
        self.profile = validate_perms(request, self.permissions)
        if request.GET.get('next', None):
            self.redirect_to = request.GET['next']
        else:
            self.redirect_to = reverse('manage_event_list',
                                       urlconf='gbe.scheduling.urls')
        if "occurrence_id" in kwargs:
            result = get_occurrence(int(kwargs['occurrence_id']))
            if result.errors and len(result.errors) > 0:
                show_general_status(
                    request,
                    result,
                    self.__class__.__name__)
                return HttpResponseRedirect(self.redirect_to)
            else:
                self.occurrence = result.occurrence

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url

        title = str(self.occurrence)
        start_time = self.occurrence.start_time
        gbe_event = self.occurrence.eventitem

        result = delete_occurrence(self.occurrence.pk)
        show_general_status(request, result, self.__class__.__name__)

        if len(result.errors) == 0:
            result = get_occurrences(
                foreign_event_ids=[self.occurrence.foreign_event_id])
            if len(result.occurrences) == 0:
                gbe_event.visible = False
                gbe_event.save()

            user_message = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="DELETE_SUCCESS",
                defaults={
                    'summary': "Occurrence Deletion Completed",
                    'description': "This event has been deleted."})
            messages.success(
                request,
                '%s<br>Title: %s,<br> Start Time: %s' % (
                    user_message[0].description,
                    title,
                    start_time.strftime(
                        GBE_DATETIME_FORMAT)))
        return HttpResponseRedirect(self.redirect_to)

    def dispatch(self, *args, **kwargs):
        return super(DeleteEventView, self).dispatch(*args, **kwargs)
