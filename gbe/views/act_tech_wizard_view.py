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
)
from scheduler.idd import (
    get_occurrences,
    get_schedule,
)


class ActTechWizardView(View):
    template = 'gbe/act_tech_wizard.tmpl'
    permissions = ('Tech Crew', )
    default_event_type = None
    page_title = 'Edit Act Technical Information'
    first_title = 'Rehearsal and Basic Information'

    def set_rehearsal_forms(self):
        rehearsal_forms = []
        possible_rehearsals = GenericEvent.objects.filter(
            type='Rehearsal Slot',
            e_conference=self.act.b_conference).values_list('eventitem_id')
        for show in self.shows:
            initial = {
                'show_private': show.pk,
                'rehearsal_label': "Rehearsal for %s" % str(show.eventitem),
                'rehearsal_choices': []}

            response = get_occurrences(
                labels=[self.act.b_conference.conference_slug],
                foreign_event_ids=possible_rehearsals,
                parent_event_id=show.pk)
            for event in response.occurrences:
                if (show.pk in self.rehearsals) and (
                        event == self.rehearsals[show.pk]):
                    initial['rehearsal_choices'] += [(
                        event.pk, 
                        date_format(event.starttime, "TIME_FORMAT"))]
                    initial['rehearsal'] = event.pk
                elif event.has_act_opening():
                    initial['rehearsal_choices'] += [(
                        event.pk, 
                        date_format(event.starttime, "TIME_FORMAT"))]
            rehearsal_forms += [BasicRehearsalForm(
                prefix=str(show.pk),
                initial=initial)]
        return rehearsal_forms

    def make_context(self, basic_form):
        basic_instructions = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="BASIC_INSTRUCTIONS",
                defaults={
                    'summary': "Basic Instructions",
                    'description': default_basic_acttech_instruct})
        basics = self.set_rehearsal_forms()
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
                self.rehearsals[show_key] = item.event

    @never_cache
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        if 'rehearsal' in request.POST:
            rehearsal = get_object_or_404(sEvent,
                                          id=request.POST['rehearsal'])
            show = get_object_or_404(
                Show,
                eventitem_id=request.POST['show_private']
                ).scheduler_events.first()
            act.set_rehearsal(show, rehearsal)
        basic_form = BasicActTechForm(request.POST,
                                      instance=self.act.tech)
        if basic_form.is_valid():
            basic_form.save()
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

        return render(request, self.template, self.make_context(basic_form))

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
        return render(request, self.template, self.make_context(
            BasicActTechForm(instance=self.act.tech, initial={
                'prop_setup': prop_initial})))

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActTechWizardView, self).dispatch(*args, **kwargs)
