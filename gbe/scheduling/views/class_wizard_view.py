from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import HiddenInput
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.core.urlresolvers import reverse
from gbe.scheduling.forms import (
    ClassBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
)
from gbe.views.class_display_functions import get_scheduling_info
from gbe.models import Class
from gbe.scheduling.views import EventWizardView
from gbe.duration import Duration
from datetime import timedelta
from django.contrib import messages
from gbe.models import UserMessage
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)


class ClassWizardView(EventWizardView):
    template = 'gbe/scheduling/class_wizard.tmpl'
    roles = ['Teacher', 'Volunteer', 'Moderator', 'Panelist', ]
    default_event_type = "conference"

    def groundwork(self, request, args, kwargs):
        context = super(ClassWizardView,
                        self).groundwork(request, args, kwargs)
        context['event_type'] = "Conference Class"
        context['second_title'] = "Pick the Class"
        return context

    def make_formset(self, working_class=None, post=None):
        if working_class:
            if working_class.type == 'Panel':
                formset = super(ClassWizardView, self).make_formset(
                    ['Moderator',
                     'Panelist',
                     'Panelist',
                     'Panelist',
                     'Panelist'],
                    initial={
                        'role': 'Moderator',
                        'worker': working_class.teacher},
                    post=post)
            else:
                formset = super(ClassWizardView, self).make_formset(
                    ['Teacher',
                     'Teacher',
                     'Teacher'],
                    initial={
                        'role': 'Teacher',
                        'worker': working_class.teacher},
                    post=post)
        else:
                formset = super(ClassWizardView, self).make_formset(
                    ['Teacher',
                     'Moderator',
                     'Panelist',
                     'Panelist',
                     'Panelist'],
                    post=post)
        return formset

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            initial={'conference':  self.conference})
        return render(request, self.template, context)

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        working_class = None
        context = self.groundwork(request, args, kwargs)
        context['second_form'] = PickClassForm(
            request.POST,
            initial={'conference':  self.conference})
        context['third_title'] = "Make New Class"
        if 'pick_class' in request.POST.keys() and context[
                'second_form'].is_valid():
            if context['second_form'].cleaned_data[
                    'accepted_class']:
                working_class = context['second_form'].cleaned_data[
                    'accepted_class']
                context['third_title'] = "Book Class:  %s" % (
                    working_class.e_title)
                context['third_form'] = ClassBookingForm(
                    instance=working_class)
                duration = working_class.duration.total_seconds(
                    ) / timedelta(hours=1).total_seconds()
                context['scheduling_info'] = get_scheduling_info(working_class)
            else:
                context['third_form'] = ClassBookingForm()
                duration = 1
            context['scheduling_form'] = ScheduleOccurrenceForm(
                conference=self.conference,
                open_to_public=True,
                initial={'duration': duration, })
            context['scheduling_form'].fields[
                'max_volunteer'].widget = HiddenInput()
            context['worker_formset'] = self.make_formset(working_class)

        elif 'set_class' in request.POST.keys(
                ) and 'eventitem_id' in request.POST.keys():
            if request.POST['eventitem_id']:
                working_class = get_object_or_404(
                    Class,
                    eventitem_id=request.POST['eventitem_id'])
                context['third_title'] = "Book Class:  %s" % (
                    working_class.e_title)
                context['third_form'] = ClassBookingForm(
                    request.POST,
                    instance=working_class)
                context['scheduling_info'] = get_scheduling_info(working_class)
            else:
                context['third_form'] = ClassBookingForm(request.POST)
            context['second_form'] = PickClassForm(
                initial={'conference':  self.conference,
                         'accepted_class': working_class})
            context['scheduling_form'] = ScheduleOccurrenceForm(
                request.POST,
                conference=self.conference)
            context['scheduling_form'].fields[
                'max_volunteer'].widget = HiddenInput()
            context['worker_formset'] = self.make_formset(working_class,
                                                          post=request.POST)
            if context['third_form'].is_valid(
                    ) and context['scheduling_form'].is_valid(
                    ) and self.is_formset_valid(context['worker_formset']):
                working_class = context['third_form'].save(commit=False)
                working_class.duration = Duration(
                    minutes=context['scheduling_form'].cleaned_data[
                        'duration']*60)
                if not hasattr(working_class, 'teacher'):
                    teacher = None
                    for form in context['worker_formset']:
                        if form.cleaned_data['worker']:
                            teacher = form.cleaned_data['worker']
                            break
                    if teacher:
                        working_class.teacher = teacher
                    else:
                        user_message = UserMessage.objects.get_or_create(
                            view=self.__class__.__name__,
                            code="NEED_LEADER",
                            defaults={
                                'summary': "Need Leader for Class",
                                'description': "You must select at least " +
                                "one person to run this class."})
                        messages.error(
                            request,
                            user_message[0].description)
                        return render(request, self.template, context)
                    working_class.e_conference = self.conference
                    working_class.b_conference = self.conference

                working_class.save()
                response = self.book_event(context['scheduling_form'],
                                           context['worker_formset'],
                                           working_class)
                success = self.finish_booking(
                    request,
                    response,
                    context['scheduling_form'].cleaned_data['day'].pk)
                if success:
                    return success
        return render(request, self.template, context)
