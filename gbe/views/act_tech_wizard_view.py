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
    UserMessage,
)
from gbetext import (
    default_basic_acttech_instruct,
)


class ActTechWizardView(View):
    template = 'gbe/act_tech_wizard.tmpl'
    permissions = ('Tech Crew', )
    default_event_type = None
    page_title = 'Edit Act Technical Information'
    first_title = 'Rehearsal and Basic Information'

    def set_rehearsal_forms(self):
        rehearsal_sets = {}
        existing_rehearsals = {}
        rehearsal_forms = []

        for show in self.shows:
            re_set = show.get_open_rehearsals()
            existing_rehearsal = None
            try:
                existing_rehearsal = [
                    r for r in self.act.get_scheduled_rehearsals() if
                    r.container_event.parent_event == show][0]
            except:
                pass
            if existing_rehearsal:
                try:
                    re_set.remove(existing_rehearsal)
                except:
                    pass
                re_set.append(existing_rehearsal)
                re_set = sorted(re_set,
                            key=lambda sched_event: sched_event.starttime)
                existing_rehearsals[show] = existing_rehearsal

            if len(re_set) > 0:
                rehearsal_sets[show] = re_set

        if len(rehearsal_sets) > 0:
            for (show, r_set) in rehearsal_sets.items():
                initial = {
                    'show_private': show.eventitem_id,
                    'rehearsal_choices':
                        [(r.id, "%s: %s" % (
                            r.as_subtype.e_title,
                            (date_format(r.starttime, "TIME_FORMAT"))))
                         for r in r_set]}
                if show in existing_rehearsals:
                    initial['rehearsal'] = existing_rehearsals[show].id
                rehearsal_forms += [
                    BasicRehearsalForm(
                        initial=initial)]
        return rehearsal_forms

    def make_context(self):
        basic_instructions = UserMessage.objects.get_or_create(
                view=self.__class__.__name__,
                code="BASIC_INSTRUCTIONS",
                defaults={
                    'summary': "Basic Instructions",
                    'description': default_basic_acttech_instruct})
        basics = self.set_rehearsal_forms()
        basics += [BasicActTechForm()]
        context = {'act': self.act,
                   'shows': self.shows,
                   'basic_forms': basics,
                   'page_title': self.page_title,
                   'first_title': self.first_title,
                   'basic_instructions': basic_instructions[0].description}
        return context

    def groundwork(self, request, args, kwargs):
        profile = validate_profile(request, require=False)
        if not profile:
            return HttpResponseRedirect(reverse('profile_update',
                                        urlconf='gbe.urls'))
        act_id = kwargs.get("act_id")
        self.act = get_object_or_404(Act, id=act_id)
        if self.act.performer.contact != profile:
            validate_perms(request, self.permissions)
        self.shows = self.act.get_scheduled_shows()

    @never_cache
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        error = self.groundwork(request, args, kwargs)
        if error:
            return error
        context = self.make_context()
        return render(request, self.template, self.make_context())

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ActTechWizardView, self).dispatch(*args, **kwargs)
