from django.shortcuts import (
    render,
    get_object_or_404,
)
from django.http import HttpResponseRedirect
from scheduler.models import *
from scheduler.forms import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.core.urlresolvers import reverse
from gbe.functions import validate_perms
from scheduler.idd import get_occurrences
from gbe.scheduling.views.functions import show_general_status


@login_required
@never_cache
def schedule_acts(request, show_id=None):
    '''
    Display a list of acts available for scheduling, allows setting show/order
    '''
    validate_perms(request, ('Scheduling Mavens',))

    import gbe.models as conf

    # came from the schedule selector
    if request.method == "POST":
        show_id = request.POST.get('show_id', 'POST')

    # no show selected yet
    if show_id is None or show_id.strip() == '':
        template = 'scheduler/select_event_type.tmpl'
        show_options = EventItem.objects.all().select_subclasses()
        show_options = filter(
            lambda event: (
                type(event) == conf.Show) and (
                event.get_conference().status != 'completed'), show_options)
        return render(request, template, {'show_options': show_options})

    # came from an ActSchedulerForm
    if show_id == 'POST':
        alloc_prefixes = set([key.split('-')[0] for key in request.POST.keys()
                              if key.startswith('allocation_')])
        for prefix in alloc_prefixes:
            form = ActScheduleForm(request.POST, prefix=prefix)
            if form.is_valid():
                data = form.cleaned_data
            else:
                continue  # error, should log
            alloc = get_object_or_404(ResourceAllocation,
                                      id=prefix.split('_')[1])
            if alloc.event.pk != data['show']:
                raise Exception("alloc: %d, selected: %s" % (alloc.event.pk, data['show']))
            else:
                raise Exception("same")
            alloc.event = data['show']
            alloc.save()
            try:
                ordering = alloc.ordering
                ordering.order = data['order']
            except:
                ordering = Ordering(allocation=alloc, order=data['order'])
            ordering.save()

        return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))

    # get allocations involving the show we want
    show = get_object_or_404(conf.Show, pk=show_id)
    event = show.scheduler_events.first()

    allocations = ResourceAllocation.objects.filter(event=event)
    allocations = [a for a in allocations if type(a.resource.item) == ActItem]

    forms = []
    show_ids = conf.Show.objects.filter(
        e_conference=show.e_conference).values('eventitem_id')
    response = get_occurrences(foreign_event_ids=show_ids)
    show_general_status(request, response, "ActScheduleView")
    show_choices = []
    for occurrence in response.occurrences:
        show_choices += [(occurrence.pk, str(occurrence))]

    for alloc in allocations:
        actitem = alloc.resource.item
        act = actitem.act
        if act.accepted != 3:
            continue
        details = {}
        details['title'] = act.b_title
        details['performer'] = act.performer
        details['show'] = event
        try:
            details['order'] = alloc.ordering.order
        except:
            o = Ordering(allocation=alloc, order=0)
            o.save()
            details['order'] = 0

        forms.append([details, alloc])
    forms = sorted(forms, key=lambda f: f[0]['order'])
    new_forms = []
    for details, alloc in forms:
        new_forms.append((
            ActScheduleForm(initial=details,
                            show_choices=show_choices,
                            prefix='allocation_%d' % alloc.id),
            details['performer'].contact.user_object.is_active))

    template = 'scheduler/act_schedule.tmpl'
    return render(request,
                  template,
                  {'forms': new_forms})
