from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.forms import HiddenInput
from django.contrib import messages
from scheduler.idd import (
    get_conflicts,
    remove_booking,
    set_person,
    test_booking,
)
from gbe.models import (
    Profile,
    UserMessage,
)
from gbe.email.functions import send_schedule_update_mail
from gbetext import volunteer_allocate_email_fail_msg
from gbe.scheduling.forms import WorkerAllocationForm
from gbe.scheduling.views.functions import show_scheduling_booking_status
from gbe.functions import eligible_volunteers
from gbe_forms_text import rank_interest_options
from scheduler.data_transfer import (
    Error,
    PersonResponse,
    Person,
)


class ManageWorkerView(View):
    ''' This must be a parent to another class.  The subclass should describe
        the settings and visualization for the volunteer event being staffed
        here.   The contract for the child is to implement a 'groundwork'
        function and provide:
        REQUIRED
            - self.conference - the conference for which the vol opp is being
                managed
            - self.manage_worker_url - the URL used to call this post function
            - self.success_url - the URL to redirect to in the event of success
            - 'make_context' to build the error context when an error occurrs
            - self.template - what will be rendered
        OPTIONAL
            - window_controls = list of controls for panels in the page, if
            adding panels, include turning them on and off via the errorcontext
            and the request.GET parameters.  If no panels are on, all panels
            will be opened.
    '''

    vol_permissions = ('Volunteer Coordinator',)
    window_controls = ['start_open', 'worker_open']

    def make_context(self, request, errorcontext=None):
        context = {}
        vol_open = False
        all_closed = True

        if errorcontext is not None:
            context = errorcontext
        context['edit_url'] = self.success_url

        for window_control in self.window_controls:
            if ((errorcontext and window_control in errorcontext
                 ) and errorcontext[window_control]) or request.GET.get(
                    window_control,
                    False) in ["True", "true", "T", "t", True]:
                context[window_control] = True
                all_closed = False

        if all_closed:
            for window_control in self.window_controls:
                context[window_control] = True

        return context

    def get_worker_allocation_forms(self, errorcontext=None):
        '''
        Returns a list of allocation forms for a volunteer opportunity
        Each form can be used to schedule one worker. Initially, must
        allocate one at a time.
        '''
        forms = []
        for person in self.occurrence.people:
            if (errorcontext and
                    'worker_alloc_forms' in errorcontext and
                    errorcontext['worker_alloc_forms'].cleaned_data[
                        'alloc_id'] == person.booking_id):
                forms.append(errorcontext['worker_alloc_forms'])
            else:
                try:
                    forms.append(WorkerAllocationForm(
                        initial={
                            'worker': Profile.objects.get(pk=person.public_id),
                            'role': person.role,
                            'label': person.label,
                            'alloc_id': person.booking_id}))
                except Profile.DoesNotExist:
                    pass
        if errorcontext and 'new_worker_alloc_form' in errorcontext:
            forms.append(errorcontext['new_worker_alloc_form'])
        else:
            forms.append(WorkerAllocationForm(initial={'role': 'Volunteer',
                                                       'alloc_id': -1}))
        return {'worker_alloc_forms': forms,
                'worker_alloc_headers': ['Worker', 'Role', 'Notes'],
                'manage_worker_url': self.manage_worker_url}

    def get_volunteer_info(self):
        volunteer_set = []
        for volunteer in eligible_volunteers(
                self.occurrence.start_time,
                self.occurrence.end_time,
                self.item.e_conference):
            assign_form = WorkerAllocationForm(
                initial={'role': 'Volunteer',
                         'worker': volunteer.profile,
                         'alloc_id': -1})
            assign_form.fields['worker'].widget = HiddenInput()
            assign_form.fields['label'].widget = HiddenInput()
            if volunteer.volunteerinterest_set.filter(
                        interest=self.occurrence.as_subtype.volunteer_type
                        ).exists():
                rank = volunteer.volunteerinterest_set.get(
                    interest=self.occurrence.as_subtype.volunteer_type).rank
            else:
                rank = 0
            conflict_response = get_conflicts(
                self.occurrence,
                volunteer.profile.user_object,
                labels=[self.conference.conference_slug])
            conflicts = None
            if hasattr(conflict_response, 'occurrences'):
                conflicts = conflict_response.occurrences

            volunteer_set += [{
                'display_name': volunteer.profile.display_name,
                'interest': rank_interest_options[rank],
                'available': volunteer.check_available(
                    self.occurrence.start_time,
                    self.occurrence.end_time),
                'conflicts': conflicts,
                'id': volunteer.pk,
                'assign_form': assign_form
            }]
        return {'eligible_volunteers': volunteer_set}

    def make_post_response(self,
                           request,
                           response=None,
                           errorcontext=None):
        if response and hasattr(response, 'booking_id'):
            show_scheduling_booking_status(
                request,
                response,
                self.__class__.__name__)
            self.success_url = "%s?worker_open=True" % self.success_url
            if response.booking_id:
                self.success_url = "%s&changed_id=%d" % (
                    self.success_url,
                    response.booking_id)
            return HttpResponseRedirect(self.success_url)
        return render(request,
                      self.template,
                      self.make_context(request, errorcontext))

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = WorkerAllocationForm(request.POST)
        response = None
        email_status = None
        if not form.is_valid():
            context = None
            if request.POST['alloc_id'] == '-1':
                form.data['alloc_id'] = -1
                context = {'new_worker_alloc_form': form}
            else:
                is_present = test_booking(
                    int(request.POST['alloc_id']), self.occurrence.pk)
                if not is_present:
                    response = PersonResponse(errors=[Error(
                        code="BOOKING_NOT_FOUND",
                        details="Booking id %s for occurrence %d not found" % (
                            request.POST['alloc_id'], self.occurrence.pk)), ])
                context = {'worker_alloc_forms': form}
            return self.make_post_response(request,
                                           response=response,
                                           errorcontext=context)
        else:
            data = form.cleaned_data
            if 'delete' in request.POST.keys():
                if ('alloc_id' not in request.POST) or (len(
                        request.POST['alloc_id']) == 0):
                    return self.make_post_response(
                        request,
                        PersonResponse(errors=[Error(
                            code="NO_BOOKING",
                            details="No booking id for occurrence id %d." % (
                                self.occurrence.pk))]))
                response = remove_booking(
                    self.occurrence.pk,
                    booking_id=int(request.POST['alloc_id']))
                if response.booking_id:
                    email_status = send_schedule_update_mail(
                        "Volunteer", data['worker'].workeritem.as_subtype)
            elif data.get('worker', None):
                if data['role'] == "Volunteer":
                    data['worker'].workeritem.as_subtype.check_vol_bid(
                        self.item.e_conference)
                person = Person(
                    user=data['worker'].workeritem.as_subtype.user_object,
                    public_id=data['worker'].workeritem.as_subtype.pk,
                    role=data['role'],
                    label=data['label'],
                    worker=None)
                if int(data['alloc_id']) > -1:
                    person.booking_id = int(data['alloc_id'])
                response = set_person(
                    self.occurrence.pk,
                    person
                )
                email_status = send_schedule_update_mail("Volunteer",
                                                         data['worker'])
            if email_status:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="EMAIL_FAILURE",
                    defaults={
                        'summary': "Email Failed",
                        'description': volunteer_allocate_email_fail_msg})
                messages.error(
                    request,
                    user_message[0].description)
            self.success_url = reverse('edit_event',
                                       urlconf='gbe.scheduling.urls',
                                       args=[self.conference.conference_slug,
                                             self.occurrence.pk])
        return self.make_post_response(request,
                                       response=response)
