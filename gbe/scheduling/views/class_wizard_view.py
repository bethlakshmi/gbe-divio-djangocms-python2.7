from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.forms import (
    HiddenInput,
    IntegerField,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from gbe.scheduling.forms import (
    ClassBookingForm,
    PickClassForm,
    ScheduleOccurrenceForm,
)
from gbe.views.class_display_functions import get_scheduling_info
from gbe.models import Class
from gbe.scheduling.views import EventWizardView
from datetime import timedelta
from django.contrib import messages
from gbe.models import UserMessage
from gbe_forms_text import (
    classbid_labels,
    class_schedule_options,
)
from gbe.scheduling.views.functions import get_start_time
from scheduler.data_transfer import Person
from scheduler.idd import create_occurrence


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

    def setup_third_form(self, working_class=None):
        context = {}
        if working_class is not None:
            context['third_title'] = "Book Class:  %s" % (
                working_class.b_title)
            context['third_form'] = ClassBookingForm(instance=working_class)
            duration = timedelta(
                minutes=working_class.length_minutes
                ).total_seconds() / timedelta(hours=1).total_seconds()
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
        if working_class is not None:
            context['scheduling_form'].fields['id'] = IntegerField(
                initial=working_class.pk,
                widget=HiddenInput)
        context['worker_formset'] = self.make_formset(working_class)
        return context

    def book_event(self,
                   bid,
                   scheduling_form,
                   people_formset):
        start_time = get_start_time(scheduling_form.cleaned_data)
        labels = [self.conference.conference_slug]
        labels += ["Conference"]
        people = []
        for assignment in people_formset:
            if assignment.is_valid() and assignment.cleaned_data['worker']:
                people += [Person(
                    user=assignment.cleaned_data[
                        'worker'].workeritem.as_subtype.user_object,
                    public_id=assignment.cleaned_data['worker'].workeritem.pk,
                    role=assignment.cleaned_data['role'])]
        response = create_occurrence(
            bid.b_title,
            timedelta(minutes=scheduling_form.cleaned_data['duration']*60),
            bid.type,
            start_time,
            scheduling_form.cleaned_data['max_volunteer'],
            people=people,
            locations=[scheduling_form.cleaned_data['location']],
            description=bid.b_description,
            labels=labels,
            approval=scheduling_form.cleaned_data['approval'],
            connected_class=bid.__class__.__name__,
            connected_id=bid.pk)
        return response

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = self.groundwork(request, args, kwargs)
        working_class = None
        if 'accepted_class' in request.GET:
            working_class = get_object_or_404(
                    Class,
                    pk=request.GET['accepted_class'])
            context.update(self.setup_third_form(working_class))
        context['second_form'] = PickClassForm(
            initial={'conference':  self.conference,
                     'accepted_class': working_class})
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
        if 'pick_class' in list(request.POST.keys()) and context[
                'second_form'].is_valid():
            working_class = None
            if context['second_form'].cleaned_data['accepted_class']:
                working_class = context['second_form'].cleaned_data[
                    'accepted_class']
            context.update(self.setup_third_form(working_class))

        elif 'set_class' in list(request.POST.keys()):
            if 'id' in list(request.POST.keys()) and request.POST['id']:
                working_class = get_object_or_404(Class, id=request.POST['id'])
                context['third_title'] = "Book Class:  %s" % (
                    working_class.b_title)
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
                working_class.duration = timedelta(
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
                    working_class.b_conference = self.conference

                working_class.save()
                response = self.book_event(
                    working_class,
                    context['scheduling_form'],
                    context['worker_formset'])
                success = self.finish_booking(
                    request,
                    response,
                    context['scheduling_form'].cleaned_data['day'].pk)
                if success:
                    return success

        return render(request, self.template, context)
