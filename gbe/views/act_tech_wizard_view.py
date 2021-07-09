from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.formats import date_format
from django.core.management import call_command
from django.urls import reverse
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import (
    validate_perms,
    validate_profile,
)
from gbe.forms import (
    AdvancedActTechForm,
    BasicActTechForm,
    BasicRehearsalForm,
)
from gbe.models import (
    Act,
    GenericEvent,
    Show,
    UserMessage,
)
from gbetext import (
    default_act_tech_advanced_submit,
    default_act_tech_basic_submit,
    default_advanced_acttech_instruct,
    default_basic_acttech_instruct,
    default_rehearsal_booked,
    default_rehearsal_acttech_instruct,
    rehearsal_book_error,
    rehearsal_remove_confirmation,
)
from scheduler.idd import (
    get_occurrences,
    get_schedule,
    remove_booking,
    set_person,
)
from gbe.scheduling.views.functions import show_general_status
from scheduler.data_transfer import (
    Commitment,
    Person,
    ScheduleItem,
)
from django.contrib import messages
from settings import GBE_DATETIME_FORMAT


class ActTechWizardView(View):
    template = 'gbe/act_tech_wizard.tmpl'
    permissions = ('Technical Director',
                   'Producer',
                   'Stage Manager',
                   'Staff Lead')
    default_event_type = None
    page_title = 'Edit Act Technical Information'
    first_title = 'Set Rehearsal Time'
    second_title = 'Provide Technical Information'
    third_title = 'Advanced Technical Information (Optional)'

    def set_rehearsal_forms(self, request=None):
        rehearsal_forms = []
        possible_rehearsals = GenericEvent.objects.filter(
            type='Rehearsal Slot',
            e_conference=self.act.b_conference).values_list('eventitem_id')
        for show in self.shows:
            response = get_occurrences(
                labels=[self.act.b_conference.conference_slug],
                foreign_event_ids=possible_rehearsals,
                parent_event_id=show.pk)
            choices = [(-1, "No rehearsal needed")]
            initial = None
            for event in response.occurrences:
                if (show.pk in self.rehearsals) and (
                        event == self.rehearsals[show.pk].event):
                    choices += [(event.pk,
                                 date_format(event.starttime, "TIME_FORMAT"))]
                    initial = {
                        'rehearsal': event.pk,
                        'booking_id': self.rehearsals[show.pk].booking_id}
                elif event.has_commitment_space("Act"):
                    choices += [(event.pk,
                                 date_format(event.starttime, "TIME_FORMAT"))]
            if initial is None and not self.act.tech.confirm_no_rehearsal:
                initial = {'rehearsal': choices[1][0]}
            if request:
                rehearsal_form = BasicRehearsalForm(
                    request.POST,
                    prefix=str(show.pk))
            else:
                rehearsal_form = BasicRehearsalForm(
                    prefix=str(show.pk),
                    initial=initial)

            rehearsal_form.fields['rehearsal'].choices = choices
            rehearsal_form.fields['rehearsal'].label = \
                "Rehearsal for %s" % str(show.eventitem)
            rehearsal_forms += [rehearsal_form]

        return rehearsal_forms

    def book_rehearsals(self, request):
        error = False
        bookings = []
        forms = self.set_rehearsal_forms(request)
        # using the form guarantees that we've checked that the user is
        # only booking rehearsals that are open, for shows they are in.
        for rehearsal_form in forms:
            if not rehearsal_form.is_valid():
                error = True
        if error:
            return error, bookings, forms, request

        for rehearsal_form in forms:
            if int(rehearsal_form.cleaned_data['rehearsal']) >= 0:
                person = Person(
                    public_id=self.act.performer.pk,
                    role="performer",
                    commitment=Commitment(decorator_class=self.act))
                if rehearsal_form.cleaned_data['booking_id']:
                    person.booking_id = int(
                        rehearsal_form.cleaned_data['booking_id'])
                response = set_person(
                    occurrence_id=int(
                        rehearsal_form.cleaned_data['rehearsal']),
                    person=person)
                # errors are internal, and not OK to show regular user
                if response.errors:
                    error = True
                else:
                    show_general_status(request,
                                        response,
                                        self.__class__.__name__)
                self.act.tech.confirm_no_rehearsal = False
                if response.occurrence:
                    bookings += [response.occurrence]
                    self.rehearsals[int(rehearsal_form.prefix)] = ScheduleItem(
                        event=response.occurrence,
                        booking_id=response.booking_id)
            else:
                if rehearsal_form.cleaned_data['booking_id']:
                    response = remove_booking(
                        occurrence_id=self.rehearsals[int(
                            rehearsal_form.prefix)].event.pk,
                        booking_id=int(
                            rehearsal_form.cleaned_data['booking_id']))
                    # errors are internal, and not OK to show regular user
                    if response.errors:
                        error = True
                    else:
                        del self.rehearsals[int(rehearsal_form.prefix)]
                        success = UserMessage.objects.get_or_create(
                            view=self.__class__.__name__,
                            code="REHEARSAL_REMOVED",
                            defaults={
                                'summary': "User Canceled Rehearsal",
                                'description': rehearsal_remove_confirmation})
                        messages.success(request, success[0].description)
                self.act.tech.confirm_no_rehearsal = True
                self.act.tech.save()
        # if there has been no failure, we've changed the state of rehearsal
        # bookings, and the forms should be changed to reflect the new
        # persistent state - BUG found on 7/9/21 with GBE-238
        if not error:
            forms = self.set_rehearsal_forms()
        return error, bookings, forms, request

    def make_context(self,
                     rehearsal_forms=None,
                     basic_form=None,
                     advanced_form=None):
        rehearsal_instruct = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="REHEARSAL_INSTRUCTIONS",
                defaults={
                    'summary': "Rehearsal Instructions",
                    'description': default_rehearsal_acttech_instruct})
        if not rehearsal_forms:
            rehearsal_forms = self.set_rehearsal_forms()
        context = {'act': self.act,
                   'shows': self.shows,
                   'rehearsals': self.rehearsals,
                   'rehearsal_forms': rehearsal_forms,
                   'page_title': self.page_title,
                   'first_title': self.first_title,
                   'rehearsal_instructions': rehearsal_instruct[0].description}

        if basic_form:
            context['first_title'] = "Change Rehearsal"
            tmp = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="BASIC_INSTRUCTIONS",
                defaults={
                    'summary': "Basic Instructions",
                    'description': default_basic_acttech_instruct})
            context['second_form'] = basic_form
            context['basic_instructions'] = tmp[0].description
            context['second_title'] = self.second_title
        if advanced_form:
            context['second_title'] = "Basic Technical Information"
            tmp = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="ADVANCED_INSTRUCTIONS",
                defaults={
                    'summary': "Advanced Instructions",
                    'description': default_advanced_acttech_instruct})
            context['third_form'] = advanced_form
            context['advanced_instructions'] = tmp[0].description
            context['third_title'] = self.third_title
        return context

    def groundwork(self, request, args, kwargs):
        self.shows = []
        self.rehearsals = {}
        self.next_page = request.GET.get('next',
                                         reverse('home', urlconf='gbe.urls'))
        profile = validate_profile(request, require=False)
        if not profile:
            return HttpResponseRedirect(reverse('profile_update',
                                        urlconf='gbe.urls'))
        act_id = kwargs.get("act_id")
        self.act = get_object_or_404(Act, id=act_id)
        if self.act.performer.contact != profile:
            validate_perms(request, self.permissions)
        response = get_schedule(labels=[self.act.b_conference.conference_slug],
                                commitment=self.act)

        for item in response.schedule_items:
            # group acts will have multiple items for same show
            if item.event not in self.shows and Show.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id).exists():
                self.shows += [item.event]
            elif GenericEvent.objects.filter(
                    eventitem_id=item.event.eventitem.eventitem_id,
                    type='Rehearsal Slot').exists():
                show_key = item.event.container_event.parent_event.pk
                self.rehearsals[show_key] = item
        if len(self.shows) == 0:
            raise Http404

    def rehearsal_booked(self):
        all_booked = True
        for show in self.shows:
            if show.pk not in self.rehearsals:
                all_booked = False
        return all_booked

    def get_initial_basic_form(self):
        if len(self.act.tech.prop_setup.strip()) > 0:
            prop_initial = eval(self.act.tech.prop_setup)
        else:
            prop_initial = []
        return BasicActTechForm(instance=self.act.tech, initial={
            'prop_setup': prop_initial,
            'confirm_no_music': int(self.act.tech.confirm_no_music)})

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error

        if ('book' in list(request.POST.keys())) or (
                'book_continue' in list(request.POST.keys())):
            error, bookings, rehearsal_forms, request = self.book_rehearsals(
                request)
            if not error:
                for occurrence in bookings:
                    rehearsal_success = UserMessage.objects.get_or_create(
                        view=self.__class__.__name__,
                        code="REHEARSAL_BOOKED",
                        defaults={
                            'summary': "Rehearsal Booked",
                            'description': default_rehearsal_booked})
                    messages.success(
                        request,
                        "%s  Rehearsal Name:  %s, Start Time: %s" % (
                            rehearsal_success[0].description,
                            str(occurrence),
                            occurrence.starttime.strftime(GBE_DATETIME_FORMAT)
                            ))
                if 'book_continue' in list(request.POST.keys()):
                    basic_form = self.get_initial_basic_form()
                    return render(request,
                                  self.template,
                                  self.make_context(rehearsal_forms,
                                                    basic_form))
            else:
                rehearsal_error = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="REHEARSAL_BOOKING_ERROR",
                    defaults={
                        'summary': "Rehearsal Booking Error",
                        'description': rehearsal_book_error})
                messages.error(request, rehearsal_error[0].description)
                return render(request,
                              self.template,
                              self.make_context(rehearsal_forms))
        elif ('finish_basics' in list(request.POST.keys())) or (
              'finish_to_advanced' in list(request.POST.keys())):
            basic_form = BasicActTechForm(request.POST,
                                          request.FILES,
                                          instance=self.act.tech)
            if basic_form.is_valid():
                basic_form.save()
                # fix or remove
                # call_command('sync_audio_downloads', unsync_all=True)
                success = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="ACT_TECH_BASIC_SUMBITTED",
                    defaults={
                        'summary': "Act Tech Basic Submitted",
                        'description': default_act_tech_basic_submit})
                messages.success(request, success[0].description)
                if 'finish_to_advanced' in list(request.POST.keys()):
                    advanced_form = AdvancedActTechForm(instance=self.act.tech)
                    return render(request, self.template, self.make_context(
                        basic_form=basic_form,
                        advanced_form=advanced_form))
            else:
                return render(request,
                              self.template,
                              self.make_context(basic_form=basic_form))
        else:
            advanced_form = AdvancedActTechForm(request.POST,
                                                instance=self.act.tech)
            if advanced_form.is_valid():
                advanced_form.save()
                # fix or remove
                # call_command('sync_audio_downloads', unsync_all=True)
                success = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="ACT_TECH_ADVANCED_SUMBITTED",
                    defaults={
                        'summary': "Act Tech Advanced Submitted",
                        'description': default_act_tech_advanced_submit})
                messages.success(request, success[0].description)
            else:
                return render(request, self.template, self.make_context(
                    basic_form=self.get_initial_basic_form(),
                    advanced_form=advanced_form))
        return HttpResponseRedirect(self.next_page)

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error

        basic_form = None
        advanced_form = None
        if self.rehearsal_booked():
            basic_form = self.get_initial_basic_form()
            if self.act.tech.is_complete:
                advanced_form = AdvancedActTechForm(instance=self.act.tech)

        return render(request, self.template, self.make_context(
            basic_form=basic_form,
            advanced_form=advanced_form))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActTechWizardView, self).dispatch(*args, **kwargs)
