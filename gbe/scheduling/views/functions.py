import pytz
from datetime import (
    datetime,
    time,
    timedelta,
)
from gbe.functions import (
    get_conference_day,
    make_warning_msg,
    validate_perms,
)
from django.shortcuts import (
    get_object_or_404,
)
from django.urls import reverse
from gbe.scheduling.forms import (
    EventBookingForm,
    ScheduleOccurrenceForm,
)
from scheduler.data_transfer import Person
from scheduler.idd import (
    get_occurrence,
    get_occurrences,
    get_people,
    update_occurrence,
)
from django.contrib import messages
from gbe.models import (
    Act,
    Conference,
    Event,
    Performer,
    Profile,
    UserMessage,
)
from settings import (
    EVALUATION_WINDOW,
    GBE_DATETIME_FORMAT,
)
from django.http import Http404
from gbetext import event_labels
from gbe_forms_text import event_settings


def get_start_time(data):
    day = data['day'].day
    time_parts = list(map(int, data['time'].split(":")))
    starttime = time(*time_parts)
    return datetime.combine(day, starttime)


#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's a warning - user gets 1 warning colored msg per warning
#      - if there's an error - user gets 1 red error message per error
# These messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_general_status(request, status_response, view, show_user=True):
    for error in status_response.errors:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code=error.code,
                defaults={
                    'summary': error.code,
                    'description': error.code})
        messages.error(
            request,
            '%s  %s' % (user_message[0].description, error.details))

    for warning in status_response.warnings:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code=warning.code,
                defaults={
                    'summary': warning.code,
                    'description': warning.code})
        messages.warning(request, '%s  %s' % (
            user_message[0].description,
            make_warning_msg(warning, use_user=show_user)))


#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's an occurrence - user gets a green success
#      - sets warnings & errors (see show_general_status)
# These three messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_scheduling_occurrence_status(request, occurrence_response, view):
    show_general_status(request, occurrence_response, view)
    if occurrence_response.occurrence:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code="OCCURRENCE_UPDATE_SUCCESS",
                defaults={
                    'summary': "Occurrence has been updated",
                    'description': "Occurrence has been updated."})
        messages.success(
            request,
            '%s<br>%s, Start Time: %s' % (
                user_message[0].description,
                str(occurrence_response.occurrence),
                occurrence_response.occurrence.starttime.strftime(
                    GBE_DATETIME_FORMAT)))


#
# Takes the HTTP Request from the view and builds the following user messages,
#   based upon the nature of the occurrence_response from scheduling:
#      - if there's a booking - user gets a green success
#      - sets warnings & errors (see show_general_status)
# These three messages are not mutually exclusive.  Order of operation is most
#   severe (error) to least severe (success)
#
def show_scheduling_booking_status(request,
                                   booking_response,
                                   view):
    show_general_status(request, booking_response, view)

    if booking_response.booking_id:
        user_message = UserMessage.objects.get_or_create(
                view=view,
                code="BOOKING_UPDATE_SUCCESS",
                defaults={
                    'summary': "Update successful",
                    'description': "User has been assigned to " +
                    "or deleted from the event"})
        messages.success(
            request,
            user_message[0].description)


def get_event_display_info(eventitem_id):
    '''
    Helper for displaying a single of event.
    '''
    try:
        item = Event.objects.get_subclass(eventitem_id=eventitem_id)
    except Event.DoesNotExist:
        raise Http404
    bio_grid_list = []
    featured_grid_list = []
    response = get_people(foreign_event_ids=[eventitem_id],
                          roles=["Performer"])
    for casting in response.people:
        act = Act.objects.get(pk=casting.commitment.class_id)
        if len(casting.commitment.role):
            featured_grid_list += [{
                'bio': act.bio,
                'role': casting.commitment.role}]
        else:
            bio_grid_list += [act.bio]

    booking_response = get_people(
        foreign_event_ids=[eventitem_id],
        roles=['Teacher', 'Panelist', 'Moderator', 'Staff Lead'])
    people = []
    if len(booking_response.people) == 0 and (
            item.__class__.__name__ == "Class"):
        people = [{
            'role': "Presenter",
            'person': item.teacher, }]
    else:
        id_set = []
        for person in booking_response.people:
            if person.public_id not in id_set:
                id_set += [person.public_id]
                people += [{
                    'role': person.role,
                    'person': eval(person.public_class).objects.get(
                        pk=person.public_id),
                }]

    eventitem_view = {
        'event': item,
        'scheduled_events': get_occurrences(
            foreign_event_ids=[eventitem_id]).occurrences,
        'bio_grid_list': bio_grid_list,
        'featured_grid_list': featured_grid_list,
        'people': people}
    return eventitem_view


#
#  EDIT EVENT FUNCTIONS
#
#  Common code between edit_event and edit_volunteer - I don't want to try
#  multiple inheritance so this is my way to avoid replicating code
#
def shared_groundwork(request, kwargs, permissions):
    conference = None
    occurrence_id = None
    occurrence = None
    item = None
    profile = validate_perms(request, permissions)
    if "conference" in kwargs:
        conference = get_object_or_404(
            Conference,
            conference_slug=kwargs['conference'])

    if "occurrence_id" in kwargs:
        occurrence_id = int(kwargs['occurrence_id'])
        result = get_occurrence(occurrence_id)
        if result.errors and len(result.errors) > 0:
            show_scheduling_occurrence_status(
                    request,
                    result,
                    "EditEventView")
            return None
        else:
            occurrence = result.occurrence
        item = get_object_or_404(
            Event,
            eventitem_id=occurrence.foreign_event_id).child()
    return (profile, occurrence, item)


def setup_event_management_form(
        conference,
        item,
        occurrence,
        context,
        open_to_public=True):
    duration = float(item.duration.total_seconds())/timedelta(
        hours=1).total_seconds()
    initial_form_info = {
        'duration': duration,
        'max_volunteer': occurrence.max_volunteer,
        'day': get_conference_day(
            conference=conference,
            date=occurrence.starttime.date()),
        'time': occurrence.starttime.strftime("%H:%M:%S"),
        'location': occurrence.location,
        'occurrence_id': occurrence.pk,
        'approval': occurrence.approval_needed}
    context['event_id'] = occurrence.pk
    context['eventitem_id'] = item.eventitem_id

    # if there was an error in the edit form
    if 'event_form' not in context:
        context['event_form'] = EventBookingForm(instance=item)
    if 'scheduling_form' not in context:
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=conference,
            open_to_public=open_to_public,
            initial=initial_form_info)
    return (context, initial_form_info)


def update_event(scheduling_form, occurrence_id, people_formset=[]):
    start_time = get_start_time(scheduling_form.cleaned_data)
    people = []
    for assignment in people_formset:
        if assignment.is_valid() and assignment.cleaned_data['worker']:
            people += [Person(
                user=assignment.cleaned_data[
                    'worker'].workeritem.as_subtype.user_object,
                public_id=assignment.cleaned_data['worker'].workeritem.pk,
                role=assignment.cleaned_data['role'])]
    response = update_occurrence(
        occurrence_id,
        start_time,
        scheduling_form.cleaned_data['max_volunteer'],
        people=people,
        locations=[scheduling_form.cleaned_data['location']],
        approval=scheduling_form.cleaned_data['approval'])
    return response


def process_post_response(request,
                          slug,
                          item,
                          start_success_url,
                          next_step,
                          occurrence_id,
                          additional_validity=True,
                          people_forms=[]):
    success_url = start_success_url
    context = {}
    response = None
    context['event_form'] = EventBookingForm(request.POST,
                                             instance=item)
    context['scheduling_form'] = ScheduleOccurrenceForm(
        request.POST,
        conference=item.e_conference,
        open_to_public=event_settings[item.type.lower()]['open_to_public'])

    if context['event_form'].is_valid(
            ) and context['scheduling_form'].is_valid(
            ) and additional_validity:
        new_event = context['event_form'].save(commit=False)
        new_event.duration = timedelta(
            minutes=context['scheduling_form'].cleaned_data[
                'duration']*60)
        new_event.save()
        response = update_event(context['scheduling_form'],
                                occurrence_id,
                                people_forms)
        if request.POST.get('edit_event', 0) != "Save and Continue":
            success_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[slug]),
                slug,
                context['scheduling_form'].cleaned_data['day'].pk,
                str([occurrence_id]),)
        else:
            success_url = "%s?%s=True" % (success_url, next_step)
    else:
        context['start_open'] = True
    return context, success_url, response


def build_icon_links(occurrence,
                     eval_occurrences,
                     calendar_type,
                     conf_completed,
                     personal_schedule_items):
    evaluate = None
    highlight = None
    role = None
    vol_disable_msg = None
    favorite_link = reverse('set_favorite',
                            args=[occurrence.pk, 'on'],
                            urlconf='gbe.scheduling.urls')
    volunteer_link = reverse('set_volunteer',
                             args=[occurrence.pk, 'on'],
                             urlconf='gbe.scheduling.urls')
    if occurrence.extra_volunteers() >= 0:
        volunteer_link = "disabled"
        vol_disable_msg = "This event has all the volunteers it needs."
    if (calendar_type == 'Conference') and (
            occurrence.start_time < (datetime.now() - timedelta(
                hours=EVALUATION_WINDOW))) and (eval_occurrences is not None):
        if occurrence in eval_occurrences:
            evaluate = "disabled"
        else:
            evaluate = reverse('eval_event',
                               args=[occurrence.pk, ],
                               urlconf='gbe.scheduling.urls')
    # when the conference is over, we only need the eval link for conf classes
    if not conf_completed or (
            conf_completed and calendar_type == 'Conference'):
        for booking in personal_schedule_items:
            if booking.event == occurrence:
                highlight = booking.role.lower()
                if booking.role == "Interested":
                    favorite_link = reverse(
                        'set_favorite',
                        args=[occurrence.pk, 'off'],
                        urlconf='gbe.scheduling.urls')
                else:
                    favorite_link = "disabled"
                    evaluate = None

                if booking.role in ("Volunteer", "Pending Volunteer"):
                    volunteer_link = reverse(
                        'set_volunteer',
                        args=[occurrence.pk, 'off'],
                        urlconf='gbe.scheduling.urls')
                elif booking.role in ("Rejected"):
                    volunteer_link = "disabled"
                    vol_disable_msg = "Thank you for volunteering. " + \
                        "You were not accepted for this shift."
                elif booking.role in ("Waitlisted"):
                    volunteer_link = "disabled"
                    vol_disable_msg = "Thank you for volunteering. " + \
                        "You were waitlisted for this shift."
                else:
                    volunteer_link = "disabled"
    if conf_completed or calendar_type == 'Volunteer':
        favorite_link = None
    if calendar_type == 'Volunteer' and occurrence.end_time < datetime.now():
        volunteer_link = None
    if occurrence.max_volunteer == 0:
        volunteer_link = None

    return (favorite_link,
            volunteer_link,
            evaluate,
            highlight,
            vol_disable_msg)
