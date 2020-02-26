from django.views.generic import View
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.utils.formats import date_format
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.functions import (
    validate_perms,
    validate_profile,
)
from django.core.urlresolvers import reverse
from gbe.forms import (
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
    default_basic_acttech_instruct,
    default_rehearsal_error,
)
from scheduler.idd import (
    get_occurrences,
    get_schedule,
    remove_booking,
    set_act,
)
from scheduler.data_transfer import BookableAct
from django.contrib import messages



class ActTechWizardView(View):
    template = 'gbe/act_tech_wizard.tmpl'
    permissions = ('Tech Crew', )
    default_event_type = None
    page_title = 'Edit Act Technical Information'
    first_title = 'Rehearsal and Basic Information'

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
            choices = []
            initial = None
            for event in response.occurrences:
                if (show.pk in self.rehearsals) and (
                        event == self.rehearsals[show.pk]):
                    choices += [(event.pk, 
                                 date_format(event.starttime, "TIME_FORMAT"))]
                    initial = {'rehearsal': event.event.pk,
                               'booking_id': event.booking_id}
                elif event.has_act_opening():
                    choices += [(event.pk, 
                                 date_format(event.starttime, "TIME_FORMAT"))]
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
        error = ""
        bookings = []
        forms = self.set_rehearsal_forms(request)
        # using the form guarantees that we've checked that the user is
        # only booking rehearsals that are open, for shows they are in.
        for rehearsal_form in forms:
            if rehearsal_form.is_valid():
                bookable = BookableAct(act=self.act)
                if rehearsal_form.cleaned_data['booking_id']:
                    bookable.booking_id = \
                        rehearsal_form.cleaned_data['booking_id']
                response = set_act(
                    occurrence_id=rehearsal_form.cleaned_data['rehearsal'],
                    act=bookable)
            else:
                error = "Can't book rehearsal for %s" % str(show.eventitem)

        return error, bookings, forms

    def make_context(self, basic_form, rehearsal_forms=None):
        basic_instructions = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="BASIC_INSTRUCTIONS",
                defaults={
                    'summary': "Basic Instructions",
                    'description': default_basic_acttech_instruct})
        if not rehearsal_forms:
            basics = self.set_rehearsal_forms()
        else:
            basics = rehearsal_forms
        basics += [basic_form]
        context = {'act': self.act,
                   'shows': self.shows,
                   'basic_forms': basics,
                   'page_title': self.page_title,
                   'first_title': self.first_title,
                   'basic_instructions': basic_instructions[0].description}
        return context

    def groundwork(self, request, args, kwargs):
        self.shows = []
        self.rehearsals = {}
        profile = validate_profile(request, require=False)
        if not profile:
            return HttpResponseRedirect(reverse('profile_update',
                                        urlconf='gbe.urls'))
        act_id = kwargs.get("act_id")
        self.act = get_object_or_404(Act, id=act_id)
        if self.act.performer.contact != profile:
            validate_perms(request, self.permissions)
        response = get_schedule(labels=[self.act.b_conference.conference_slug],
                                act=self.act)

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

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        basic_form = BasicActTechForm(request.POST,
                                      instance=self.act.tech)
        if basic_form.is_valid():
            error, bookings, rehearsal_forms = self.book_rehearsals(request)
            if len(error) == 0:
                basic_form.save()
                return HttpResponseRedirect(
                    reverse('home', urlconf='gbe.urls'))
            else:
                rehearsal_fail = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="REHEARSAL_NOT_BOOKED",
                    defaults={
                        'summary': "Rehearsal Booking Error",
                        'description': default_rehearsal_error})
                messages.error(request, "%s: %s" % (
                               rehearsal_fail[0].description,
                               error))

        return render(request,
                      self.template,
                      self.make_context(basic_form, rehearsal_forms))

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        if len(self.act.tech.prop_setup.strip()) > 0:
            prop_initial = eval(self.act.tech.prop_setup)
        else:
            prop_initial = []
        basic_form = BasicActTechForm(instance=self.act.tech, initial={
            'prop_setup': prop_initial})
        return render(request, self.template, self.make_context(basic_form))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActTechWizardView, self).dispatch(*args, **kwargs)
