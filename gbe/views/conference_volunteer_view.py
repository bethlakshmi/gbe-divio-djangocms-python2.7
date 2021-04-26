from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import (
    ModelChoiceField,
    ChoiceField,
)
from gbe_logging import log_func
from gbe.models import (
    ClassProposal,
    ConferenceVolunteer,
    Performer,
)
from gbe.forms import ConferenceVolunteerForm
from gbetext import (
    conf_volunteer_save_error,
)
from gbe_forms_text import (
    class_participation_types,
    panel_participation_types,
    conference_participation_types,
)
from gbe.functions import validate_profile


@login_required
@log_func
def ConferenceVolunteerView(request):
    '''
    Volunteer to chair or sit on a panel or teach a class.
    Builds out from Class Proposal
    '''
    page_title = "Apply to Present"
    view_title = "Apply to Present"
    owner = validate_profile(request, require=False)
    if not owner:
        return HttpResponseRedirect(reverse('profile_update',
                                            urlconf='gbe.urls'))
    presenters = owner.personae.all()
    classes = ClassProposal.objects.filter(
        display=True,
        conference__status="upcoming").order_by('type', 'title')

    # if there's no classes to work with, save the user the bother, and
    # just let them know
    if len(classes) == 0:
        return render(request, 'gbe/conf_volunteer_list.tmpl',
                      {'view_title': view_title, 'page_title': page_title})
    if len(presenters) == 0:
        return HttpResponseRedirect(reverse('persona_create',
                                            urlconf='gbe.urls') +
                                    '?next=' +
                                    reverse('conference_volunteer',
                                            urlconf='gbe.urls'))
    header = ClassProposal().presenter_bid_header
    header += ConferenceVolunteer().presenter_bid_header

    if request.method == 'POST':
        for aclass in classes:
            if str(aclass.id)+'-volunteering' in list(request.POST.keys()):
                form = ConferenceVolunteerForm(request.POST,
                                               prefix=str(aclass.id))
                if not form.is_valid():
                    return render(request, 'gbe/error.tmpl',
                                  {'error': conf_volunteer_save_error})
                volunteer, created = ConferenceVolunteer.objects.get_or_create(
                    presenter=form.cleaned_data['presenter'],
                    bid=aclass,
                    defaults=form.cleaned_data)

                if not created:    # didn't create, so need to update
                    form = ConferenceVolunteerForm(request.POST,
                                                   instance=volunteer,
                                                   prefix=str(aclass.id))
                    if form.is_valid():
                        form.save()
                    else:
                        return render(request, 'gbe/error.tmpl',
                                      {'error': conf_volunteer_save_error})
        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
    else:
        how = 'how_volunteer'
        rows = []
        for aclass in classes:
            form = ConferenceVolunteerForm(
                initial={'bid': aclass, 'presenter': presenters[0]},
                prefix=str(aclass.id))
            form.fields['presenter'] = ModelChoiceField(
                queryset=Performer.
                objects.filter(contact=owner),
                empty_label=None)
            if aclass.type == "Class":
                form.fields[how] = ChoiceField(
                    choices=class_participation_types)
                form.fields[how].widget.attrs['readonly'] = True
            elif aclass.type == "Panel":
                form.fields[how] = ChoiceField(
                    choices=panel_participation_types,
                    initial="Panelist")
            else:
                form.fields[how] = ChoiceField(
                    choices=conference_participation_types)
            form.fields[how].widget.attrs['class'] = how
            bid_row = {}
            bid_row['conf_item'] = aclass.presenter_bid_info
            bid_row['form'] = form
            rows.append(bid_row)

    return render(request, 'gbe/conf_volunteer_list.tmpl',
                  {'view_title': view_title, 'page_title': page_title,
                   'header': header, 'rows': rows})
