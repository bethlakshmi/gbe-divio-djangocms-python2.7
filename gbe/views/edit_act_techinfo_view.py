from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.forms import (
    ChoiceField,
    ModelChoiceField,
)
from django.core.urlresolvers import reverse
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe_logging import log_func
from gbe.functions import (
    validate_profile,
    validate_perms,
)
from gbe_forms_text import starting_cues
from gbe.models import (
    Act,
    CueInfo,
    Performer,
    Show,
    UserMessage
    )
from gbe.forms import (
    RehearsalSelectionForm,
    ActTechInfoForm,
    AudioInfoSubmitForm,
    LightingInfoForm,
    CueInfoForm,
    VendorCueInfoForm,
    )
from scheduler.models import Event as sEvent
from gbetext import default_update_act_tech
from django.utils.formats import date_format
from django.core.management import call_command


def set_rehearsal_forms(shows, act):
    rehearsal_sets = {}
    existing_rehearsals = {}
    rehearsal_forms = []

    for show in shows:
        re_set = show.get_open_rehearsals()
        existing_rehearsal = None
        try:
            existing_rehearsal = [r for r in act.get_scheduled_rehearsals() if
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
                'show': show,
                'show_private': show.eventitem_id,
                'rehearsal_choices':
                    [(r.id, "%s: %s" % (
                        r.as_subtype.e_title,
                        (date_format(r.starttime, "TIME_FORMAT"))))
                     for r in r_set]}
            if show in existing_rehearsals:
                initial['rehearsal'] = existing_rehearsals[show].id
            rehearsal_forms += [
                RehearsalSelectionForm(
                    initial=initial)]
    return rehearsal_forms


@login_required
@log_func
@never_cache
def EditActTechInfoView(request, act_id):
    '''
    Modify tech info for an existing act
    '''
    page_title = 'Edit Act Technical Information'
    view_title = 'Edit Act Technical Information'
    submit_button = 'Submit'

    profile = validate_profile(request, require=False)
    if not profile:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls'))

    act = get_object_or_404(Act, id=act_id)
    if act.performer.contact != profile:
        validate_perms(request, ('Tech Crew', ))

    audio_info = act.tech.audio
    lighting_info = act.tech.lighting
    cue_objects = [CueInfo.objects.get_or_create(techinfo=act.tech,
                                                 cue_sequence=i)[0]
                   for i in range(3)]

    shows = act.get_scheduled_shows()
    show_detail = get_object_or_404(Show, eventitem_id=shows[0].eventitem.pk)

    if show_detail.cue_sheet == 'Theater':
        formtype = CueInfoForm
    elif show_detail.cue_sheet == 'Alternate':
        formtype = VendorCueInfoForm
    else:
        formtype = "None"

    form = ActTechInfoForm(instance=act,
                           prefix='act_tech_info')
    q = Performer.objects.filter(contact=profile)
    form.fields['performer'] = ModelChoiceField(queryset=q)

    rehearsal_forms = set_rehearsal_forms(shows, act)

    if request.method == 'POST':
        if 'rehearsal' in request.POST:
            rehearsal = get_object_or_404(sEvent,
                                          id=request.POST['rehearsal'])
            show = get_object_or_404(
                Show,
                eventitem_id=request.POST['show_private']
                ).scheduler_events.first()
            act.set_rehearsal(show, rehearsal)
        audioform = AudioInfoSubmitForm(request.POST,
                                        request.FILES,
                                        prefix='audio_info',
                                        instance=audio_info)
        lightingform = LightingInfoForm(request.POST,
                                        prefix='lighting_info',
                                        instance=lighting_info)
        cue_fail = False
        if formtype != "None":
            cue_forms = [formtype(request.POST,
                                  prefix='cue%d' % i,
                                  instance=cue_objects[i]) for i in range(3)]
            cue_forms[0].fields['cue_off_of'] = ChoiceField(
                choices=starting_cues,
                initial=starting_cues[0])
            cue_fail = not cue_forms[0].is_valid()
            for f in cue_forms:
                if f.is_valid():
                    f.save()

        techforms = [lightingform,  audioform]

        forms_valid = True
        for f in techforms:
            forms_valid = f.is_valid() and forms_valid
        if forms_valid:
            for f in techforms:
                f.save()
            call_command('sync_audio_downloads',
                         unsync_all=True)
        tech = act.tech
        if forms_valid and tech.is_complete and not cue_fail:
            user_message = UserMessage.objects.get_or_create(
                view='EditActTechInfoView',
                code="UPDATE_ACT_TECH",
                defaults={
                    'summary': "Update Act Tech Info Success",
                    'description': default_update_act_tech})
            messages.success(request, user_message[0].description)
            return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
        else:
            form_data = {'readonlyform': [form],
                         'rehearsal_forms': rehearsal_forms,
                         'forms': techforms,
                         'page_title': page_title,
                         'view_title': view_title,
                         'showheader': False,
                         'nodraft': submit_button,
                         'hide_list_details': True,
                         'cue_type': show_detail.cue_sheet
                         }
            if formtype != "None":
                form_data['cues'] = cue_forms

            return render(request,
                          'gbe/act_techinfo.tmpl',
                          form_data)
    else:
        audioform = AudioInfoSubmitForm(prefix='audio_info',
                                        instance=audio_info)
        lightingform = LightingInfoForm(prefix='lighting_info',
                                        instance=lighting_info)
        techforms = [lightingform, audioform]

        form_data = {'readonlyform': [form],
                     'rehearsal_forms': rehearsal_forms,
                     'forms': techforms,
                     'page_title': page_title,
                     'view_title': view_title,
                     'showheader': False,
                     'nodraft': submit_button,
                     'hide_list_details': True,
                     'cue_type': show_detail.cue_sheet}

        if formtype != "None":
            cue_forms = [formtype(prefix='cue%d' % i, instance=cue_objects[i])
                         for i in range(3)]
            cue_forms[0].fields['cue_off_of'] = ChoiceField(
                choices=starting_cues,
                initial=starting_cues[0])
            form_data['cues'] = cue_forms

        return render(request,
                      'gbe/act_techinfo.tmpl',
                      form_data)
