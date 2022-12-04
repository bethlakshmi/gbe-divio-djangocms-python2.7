from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from gbe.scheduling.forms import (
    CopyEventForm,
    CopyEventPickModeForm,
)
from scheduler.idd import get_occurrence
from gbe.scheduling.views.functions import (
    show_scheduling_occurrence_status,
)
from datetime import timedelta
from django.forms.utils import ErrorList
from gbe_forms_text import (
    copy_errors,
)


class CopyCollectionsView(View):
    '''
        This is an abstract view to help with copying, and remove redundant
        code.  Child views are required to have:
        - a groundwork function that creates a list of self.children, a
          start_day and checks permissions
        - a make_context that defines the first title and event_type
        - get_copy_target = returning the second title and the delta days
        - copy_root = which does whatever is needed to make a new parent root
        - copy_event = which manages chaining events to the root
    '''
    template = 'gbe/scheduling/copy_wizard.tmpl'
    copy_date_format = "%a, %b %-d, %Y %-I:%M %p"
    children = []
    start_day = None

    def make_context(self, request, context, post=None):
        if self.children and len(self.children) > 0:
            context['copy_mode'] = CopyEventPickModeForm(
                post,
                event_type=context['event_type'],
                initial={'room': context['room']})
        else:
            context = self.setup_solo(context, post)
        return context

    def validate_and_proceed(self, request, context):
        make_copy = False
        if 'copy_mode' in list(
                context.keys()) and context['copy_mode'].is_valid():
            proceed_to_second = True
            if context['copy_mode'].cleaned_data[
                    'copy_mode'] == "copy_children_only":
                context['second_title'], delta, conference = \
                    self.get_copy_target(context)
                # Because the error check requires knowing how to get the
                # target's conference
                if not context['copy_mode'].cleaned_data[
                        'room'].conferences.filter(
                            pk=conference.pk).exists():
                    errors = context['copy_mode']._errors.setdefault(
                        "room",
                        ErrorList())
                    errors.append(copy_errors['room_target_mismatch'])
                    proceed_to_second = False
            elif context['copy_mode'].cleaned_data[
                    'copy_mode'] == "include_parent":
                context['second_title'] = "Create Copy at %s: %s" % (
                    context['copy_mode'].cleaned_data[
                        'copy_to_day'].conference.conference_slug,
                    str(context['copy_mode'].cleaned_data['copy_to_day']))
                delta = context['copy_mode'].cleaned_data[
                    'copy_to_day'].day - self.start_day
            if proceed_to_second:
                context['second_form'] = self.make_event_picker(
                    request,
                    delta)
        elif 'copy_solo_mode' in list(
                context.keys()) and context['copy_solo_mode'].is_valid():
            make_copy = True
        elif 'pick_day' in list(
                context.keys()) and context['pick_day'].is_valid():
            make_copy = True
        return make_copy, context

    def make_event_picker(self, request, delta):
        form = CopyEventForm(request.POST)
        event_choices = ()
        for occurrence in self.children:
            event_choices += ((
                occurrence.pk,
                "%s - %s" % (
                    str(occurrence),
                    (occurrence.start_time + delta).strftime(
                        self.copy_date_format))),)
        form.fields['copied_event'].choices = event_choices
        return form

    def copy_events_from_form(self, request):
        form = self.make_event_picker(request, timedelta(0))
        new_root = None
        if form.is_valid():
            copied_ids = []
            alt_id = None
            room = form.cleaned_data['room']
            if form.cleaned_data['copy_mode'] == "copy_children_only":
                (new_root,
                 target_day,
                 delta,
                 conference) = self.get_child_copy_settings(form)
            elif form.cleaned_data['copy_mode'] == "include_parent":
                target_day = form.cleaned_data['copy_to_day']
                delta = target_day.day - self.start_day
                conference = form.cleaned_data['copy_to_day'].conference
                new_root = self.copy_root(
                    request,
                    delta,
                    form.cleaned_data['copy_to_day'].conference,
                    room)
                if new_root and new_root.__class__.__name__ == "Event":
                    copied_ids += [new_root.pk]
                else:
                    alt_id = new_root.pk

            for sub_event_id in form.cleaned_data["copied_event"]:
                response = get_occurrence(sub_event_id)
                labels = [conference.conference_slug]
                if response.occurrence.as_subtype.calendar_type:
                    labels += [response.occurrence.as_subtype.calendar_type]

                response = self.copy_event(
                    response.occurrence,
                    delta,
                    conference,
                    room,
                    labels,
                    new_root.pk)
                show_scheduling_occurrence_status(
                    request,
                    response,
                    self.__class__.__name__)
                if response.occurrence:
                    copied_ids += [response.occurrence.pk]
            url = "%s?%s-day=%d&filter=Filter" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[conference.conference_slug]),
                conference.conference_slug,
                target_day.pk)
            if len(copied_ids) > 0:
                url += "&new=%s" % str(copied_ids)
            if alt_id:
                url += "&alt_id=%s" % alt_id
            return HttpResponseRedirect(url)
        else:
            context = self.make_context(request, post=request.POST)
            make_copy, context = self.validate_and_proceed(request, context)
            context['second_form'] = form
            return render(request, self.template, context)

    @never_cache
    def get(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        return render(
            request,
            self.template,
            self.make_context(request))

    @never_cache
    def post(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        context = {}
        if 'pick_mode' in list(request.POST.keys()):
            context = self.make_context(request, post=request.POST)
            make_copy, context = self.validate_and_proceed(request, context)
            if make_copy:
                return self.copy_solo(request, context)
        if 'pick_event' in list(request.POST.keys()):
            return self.copy_events_from_form(request)
        return render(
            request,
            self.template,
            context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CopyCollectionsView, self).dispatch(*args, **kwargs)
