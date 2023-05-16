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
    ActCastingOption,
    Conference,
    UserMessage,
)
from settings import (
    EVALUATION_WINDOW,
    GBE_DATETIME_FORMAT,
)
from django.http import Http404
from gbe_forms_text import event_settings
from gbetext import (
    calendar_type,
    slug_safety_msgs,
)


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


def get_event_display_info(occurrence_id):
    '''
    Helper for displaying a single of event.
    '''
    response = get_occurrence(occurrence_id)
    if response.errors and response.errors[0].code == "OCCURRENCE_NOT_FOUND":
        raise Http404

    occurrence = response.occurrence
    bio_grid_list = {}
    featured_grid_list = []
    response = get_people(event_ids=[occurrence_id], roles=["Performer"])
    regular_roles = {}
    special_roles = {}
    for casting in ActCastingOption.objects.filter():
        if casting.show_as_special:
            special_roles[casting.casting] = casting.display_header
        else:
            regular_roles[casting.casting] = casting.display_header
    for casting in response.people:
        performer = eval(casting.public_class).objects.get(
            pk=casting.public_id)
        if len(casting.commitment.role) > 0 and (
                casting.commitment.role in special_roles):
            featured_grid_list += [{
                'bio': performer,
                'role': special_roles[casting.commitment.role]}]
        else:
            if len(casting.commitment.role) > 0 and (
                    casting.commitment.role in regular_roles):
                header = regular_roles[casting.commitment.role]
            else:
                header = "Fabulous Performers"

            if header in bio_grid_list:
                bio_grid_list[header] += [performer]
            else:
                bio_grid_list[header] = [performer]
    featured_grid_list.sort(key=lambda p: p['bio'].name)
    for header, perf_list in bio_grid_list.items():
        perf_list.sort(key=lambda p: p.name)

    booking_response = get_people(
        event_ids=[occurrence_id],
        roles=['Teacher', 'Panelist', 'Moderator', 'Staff Lead'])
    people = []
    id_set = []
    for person in booking_response.people:
        if person.public_id not in id_set:
            id_set += [person.public_id]
            people += [{
                'role': person.role,
                'person': eval(person.public_class).objects.get(
                    pk=person.public_id)}]

    eventitem_view = {
        'occurrence': occurrence,
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

    return (profile, occurrence)


def setup_event_management_form(
        conference,
        occurrence,
        context,
        open_to_public=True):
    duration = float(occurrence.length.total_seconds())/timedelta(
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

    # if there was an error in the edit form
    if 'event_form' not in context:
        context['event_form'] = EventBookingForm(
            initial={'slug': occurrence.slug,
                     'title': occurrence.title,
                     'description': occurrence.description})
    if 'scheduling_form' not in context:
        context['scheduling_form'] = ScheduleOccurrenceForm(
            conference=conference,
            open_to_public=open_to_public,
            initial=initial_form_info)
    return (context, initial_form_info)


def update_event(event_form,
                 scheduling_form,
                 occurrence_id,
                 roles=None,
                 people_formset=[],
                 slug=None):
    start_time = get_start_time(scheduling_form.cleaned_data)
    people = []
    for assignment in people_formset:
        if assignment.is_valid() and assignment.cleaned_data['worker']:
            people += [Person(
                user=assignment.cleaned_data[
                    'worker'].workeritem.as_subtype.user_object,
                public_id=assignment.cleaned_data['worker'].workeritem.pk,
                role=assignment.cleaned_data['role'])]
    if len(people) == 0:
        people = None
    response = update_occurrence(
        occurrence_id,
        event_form.cleaned_data['title'],
        event_form.cleaned_data['description'],
        start_time,
        length=timedelta(
            minutes=scheduling_form.cleaned_data['duration']*60),
        max_volunteer=scheduling_form.cleaned_data['max_volunteer'],
        people=people,
        roles=roles,
        locations=[scheduling_form.cleaned_data['location']],
        approval=scheduling_form.cleaned_data['approval'],
        slug=event_form.cleaned_data['slug'])
    return response


def process_post_response(request,
                          conference,
                          start_success_url,
                          next_step,
                          occurrence,
                          roles=None,
                          additional_validity=True,
                          people_forms=[]):
    success_url = start_success_url
    context = {}
    response = None
    context['event_form'] = EventBookingForm(request.POST)
    context['scheduling_form'] = ScheduleOccurrenceForm(
        request.POST,
        conference=conference,
        open_to_public=event_settings[
            occurrence.event_style.lower()]['open_to_public'])

    if context['event_form'].is_valid(
            ) and context['scheduling_form'].is_valid(
            ) and additional_validity:

        response = update_event(
            context['event_form'],
            context['scheduling_form'],
            occurrence.pk,
            roles,
            people_forms,
            slug=context['event_form'].cleaned_data['slug'])

        if request.POST.get('edit_event', 0) != "Save and Continue":
            success_url = "%s?%s-day=%d&filter=Filter&new=%s" % (
                reverse('manage_event_list',
                        urlconf='gbe.scheduling.urls',
                        args=[conference.conference_slug]),
                conference.conference_slug,
                context['scheduling_form'].cleaned_data['day'].pk,
                str([occurrence.pk]),)
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
    if occurrence.event_style == "Show":
        volunteer_link = None
    if occurrence.max_volunteer == 0:
        volunteer_link = None

    return (favorite_link,
            volunteer_link,
            evaluate,
            highlight,
            vol_disable_msg)


def setup_staff_area_saved_messages(request, title, slug, class_name):
    if slug in calendar_type.values():
        user_message = UserMessage.objects.get_or_create(
            view=class_name,
            code="STAFF_AREA_SLUG_IS_RESERVED_WORD",
            defaults={'summary': "Staff Area has a slug that overlaps " +
                      "with calendar type labels",
                      'description': slug_safety_msgs['cal_type']})
        messages.warning(
            request,
            '%s<br>Slug: %s' % (user_message[0].description, slug))
    if Conference.objects.filter(conference_slug=slug).exists():
        user_message = UserMessage.objects.get_or_create(
            view=class_name,
            code="STAFF_AREA_SLUG_ALSO_CONF_SLUG",
            defaults={'summary': "Staff Area has a slug that overlaps " +
                      "with a conference slug",
                      'description': slug_safety_msgs['conference_overlap']})
        messages.warning(
            request,
            '%s<br>Slug: %s' % (user_message[0].description, slug))
    user_message = UserMessage.objects.get_or_create(
        view=class_name,
        code="STAFF_AREA_UPDATE_SUCCESS",
        defaults={'summary': "Staff Area has been updated",
                  'description': "Staff Area has been updated."})
    messages.success(request,
                     '%s<br>Title: %s' % (user_message[0].description, title))
