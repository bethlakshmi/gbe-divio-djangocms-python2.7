from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.http import HttpResponseRedirect
from django.urls import reverse
from scheduler.idd import (
    create_occurrence,
    delete_occurrence,
    get_occurrence,
    get_occurrences,
    update_occurrence,
)
from django.views.generic import View
from gbe.scheduling.forms import VolunteerOpportunityForm
from gbe.scheduling.views.functions import (
    get_start_time,
    show_general_status,
    show_scheduling_occurrence_status,
)
from gbe.functions import get_conference_day
from django.contrib import messages
from gbe.models import UserMessage
from gbetext import calendar_for_event


class ManageVolWizardView(View):
    ''' This must be a parent to another class.  The subclass should describe
        the settings and visualization for the parent of the volunteer events
        manipulated here.   The contract for the child is to implement a
        'groundwork' function and provide:
        REQUIRED
            - self.conference - the conference for which the vol opp is being
                managed
            - any additional self.labels (a list) to be used during opp create
                - the conference slug, and appropriate calendar type will be
                made here.
            - self.manage_vol_url - the URL used to call this post function
            - self.parent_id (optional) - the id of a parent event, if null,
                there will be no parent
            - self.success_url - the URL to redirect to in the event of success
            - 'make_context' to build the error context when an error occurrs
        OPTIONAL
            - do_additional_actions - to provide additional opps related
            actions - if not provide, edit, create, delete, duplicate are
            available, if one of those functions is not provided, post will
            exit with no return value
            - window_controls = list of controls for panels in the page, if
            adding panels, include turning them on and off via the errorcontext
            and the request.GET parameters.  If no panels are on, all panels
            will be opened.
    '''

    vol_permissions = ('Volunteer Coordinator',)
    parent_id = None
    labels = []
    window_controls = ['start_open', 'volunteer_open']

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

    def get_manage_opportunity_forms(self,
                                     initial,
                                     manage_vol_info,
                                     conference,
                                     request,
                                     staff_area_id=None,
                                     errorcontext=None,
                                     occurrence_id=None,
                                     labels=[]):
        '''
        Generate the forms to allocate, edit, or delete volunteer
        opportunities associated with a scheduler event.
        '''
        actionform = []
        context = {}
        if occurrence_id is not None or len(labels) > 0:
            response = get_occurrences(parent_event_id=occurrence_id,
                                       labels=labels)
        else:
            return None

        if request.GET.get('changed_id', None):
            context['changed_id'] = int(
                self.request.GET.get('changed_id', None))

        for vol_occurence in response.occurrences:
            try:
                if (errorcontext and 'error_opp_form' in errorcontext and
                        errorcontext['error_opp_form'].cleaned_data['opp_sched_id'] == vol_occurence.pk):
                    actionform.append(errorcontext['error_opp_form'])
                else:
                    num_volunteers = vol_occurence.max_volunteer
                    date = vol_occurence.start_time.date()

                    time = vol_occurence.start_time.time
                    day = get_conference_day(
                        conference=self.conference,
                        date=date)
                    location = vol_occurence.location
                    if location:
                        room = location.room
                    elif self.occurrence.location:
                        room = self.occurrence.location.room

                    actionform.append(
                        VolunteerOpportunityForm(
                            conference=conference,
                            initial={'opp_sched_id': vol_occurence.pk,
                                     'max_volunteer': num_volunteers,
                                     'title': vol_occurence.title,
                                     'duration': vol_occurence.length,
                                     'event_style': vol_occurence.event_style,
                                     'day': day,
                                     'time': time,
                                     'location': room,
                                     'type': "Volunteer",
                                     'approval': vol_occurence.approval_needed,
                                     },
                            )
                        )
            except:
                pass
        context['actionform'] = actionform
        if staff_area_id is not None:
            context['report_url'] = reverse('staff_area',
                                            urlconf='gbe.reporting.urls',
                                            args=[staff_area_id])

        if errorcontext and 'createform' in errorcontext:
            createform = errorcontext['createform']
        else:
            createform = VolunteerOpportunityForm(
                prefix='new_opp',
                initial=initial,
                conference=conference)

        actionheaders = ['Title',
                         '#',
                         'Duration',
                         'Day',
                         'Time',
                         'Location',
                         'Approve']
        context.update({'createform': createform,
                        'actionheaders': actionheaders,
                        'manage_vol_url': manage_vol_info}),
        return context

    def make_post_response(self,
                           request,
                           response=None,
                           errorcontext=None):
        if response:
            show_scheduling_occurrence_status(
                request,
                response,
                self.__class__.__name__)

        if response and response.occurrence:
            return HttpResponseRedirect(self.success_url)
        else:
            return render(request,
                          self.template,
                          self.make_context(request, errorcontext))

    def check_success_and_return(self,
                                 request,
                                 response=None,
                                 errorcontext=None,
                                 window_controls="volunteer_open=True"):
        if response and response.occurrence:
            self.success_url = "%s?changed_id=%d" % (
                self.success_url,
                response.occurrence.pk)
            if window_controls:
                self.success_url = "%s&%s" % (self.success_url,
                                              window_controls)

        return self.make_post_response(
            request,
            response,
            errorcontext)

    def get_basic_form_settings(self):
        data = self.event_form.cleaned_data
        self.room = data['location']
        self.max_volunteer = 0
        if data['max_volunteer']:
                self.max_volunteer = data['max_volunteer']
        self.start_time = get_start_time(data)
        if 'approval' in data:
            self.approval = data['approval']
        else:
            self.approval = False
        if self.create:
            data['labels'] = self.labels + [self.conference.conference_slug]
            if calendar_for_event[data['event_style']]:
                data['labels'] += [calendar_for_event[data['event_style']]]
        return data

    def do_additional_actions(self, request):
        return None

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error_url = self.groundwork(request, args, kwargs)
        if error_url:
            return error_url
        self.create = False
        response = None
        context = None

        if ('create' in list(request.POST.keys())) or (
                'duplicate' in list(request.POST.keys())):
            self.create = True
            if 'create' in list(request.POST.keys()):
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    prefix='new_opp',
                    conference=self.conference)
            else:
                self.event_form = VolunteerOpportunityForm(
                    request.POST,
                    conference=self.conference)
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                response = create_occurrence(
                    data['title'],
                    data['duration'],
                    data['event_style'],
                    self.start_time,
                    self.max_volunteer,
                    locations=[self.room],
                    labels=data['labels'],
                    parent_event_id=self.parent_id,
                    approval=self.approval)
            else:
                context = {'createform': self.event_form,
                           'volunteer_open': True}

            return self.check_success_and_return(request,
                                                 response=response,
                                                 errorcontext=context)

        elif 'edit' in list(request.POST.keys()):
            self.event_form = VolunteerOpportunityForm(
                request.POST,
                conference=self.conference)
            if self.event_form.is_valid():
                data = self.get_basic_form_settings()
                response = update_occurrence(
                    data['opp_sched_id'],
                    title=data['title'],
                    start_time=self.start_time,
                    length=data['duration'],
                    max_volunteer=self.max_volunteer,
                    locations=[self.room],
                    approval=self.approval)
            else:
                context = {'error_opp_form': self.event_form,
                           'volunteer_open': True}

            return self.check_success_and_return(request,
                                                 response=response,
                                                 errorcontext=context)

        elif 'delete' in list(request.POST.keys()):
            response = delete_occurrence(request.POST['opp_sched_id'])
            show_general_status(request, response, self.__class__.__name__)
            if not response.errors:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="DELETE_SUCCESS",
                    defaults={
                        'summary': "Volunteer Opportunity Deleted",
                        'description': "A volunteer opportunity was deleted."})
                messages.success(request, user_message[0].description)
                return HttpResponseRedirect(self.success_url)
            else:
                return render(request,
                              self.template,
                              self.make_context(request, errorcontext))
        elif 'allocate' in list(request.POST.keys()):
            response = get_occurrence(request.POST['opp_sched_id'])
            return HttpResponseRedirect(
                reverse('edit_volunteer',
                        urlconf='gbe.scheduling.urls',
                        args=[self.conference.conference_slug,
                              request.POST['opp_sched_id']]))
        else:
            actions = self.do_additional_actions(request)
            if actions:
                return actions
            else:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="UNKNOWN_ACTION",
                    defaults={
                        'summary': "Unknown Action",
                        'description': "This is an unknown action."})
                messages.error(
                    request,
                    user_message[0].description)
                return HttpResponseRedirect(self.success_url)
