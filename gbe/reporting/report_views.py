# View functions for reporting
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.core.management import call_command
from django.views.decorators.cache import never_cache
from gbe.models import (
    Bio,
    Class,
    Conference,
    Room,
)
from scheduler.models import PeopleAllocation
from ticketing.models import Transaction
import os as os
import csv
from gbetext import (
    class_styles,
    class_roles,
    privileged_event_roles,
    not_scheduled_roles,
)
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from scheduler.idd import get_people


def list_reports(request):
    '''
      Shows listing of all reports in this area
    '''
    viewer_profile = validate_perms(request, 'any', require=True)
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()
    return render(request,
                  'gbe/report/report_list.tmpl', {
                      'conference_slugs': conference_slugs(),
                      'conference': conference,
                      'return_link': reverse('report_list',
                                             urlconf='gbe.reporting.urls')})


@never_cache
def env_stuff(request, conference_choice=None):
    '''
    Generates an envelope-stuffing report.
    '''
    reviewer = validate_perms(request, ('Registrar',))

    if conference_choice:
        conference = get_conference_by_slug(conference_choice)
    else:
        conference = get_current_conference()

    header = ['Badge Name',
              'First',
              'Last',
              'Tickets',
              'Personae',
              'Staff Lead',
              'Volunteering',
              'Presenter',
              'Show']

    people_rows = {}
    # TODO - right now, there is no great IDD that does people class/id AND
    # events.  If that is ever figured out, fix it here
    for commit in PeopleAllocation.objects.filter(
            event__eventlabel__text=conference.conference_slug).exclude(
            role__in=not_scheduled_roles+["Interested"]):
        for user in commit.people.users.filter(is_active=True):
            name = user.profile.get_badge_name().encode('utf-8').strip()
            if name not in people_rows.keys():
                people_rows[name] = {
                    'first': user.first_name.encode(
                        'utf-8').strip(),
                    'last': user.last_name.encode(
                        'utf-8').strip(),
                    'ticket_names': "",
                    'staff_lead_list': "",
                    'volunteer_list': "",
                    'class_list': "",
                    'personae_list': "",
                    'show_list': "",
                }
            if commit.role == "Staff Lead":
                people_rows[name]['staff_lead_list'] += str(commit.event)+', '
            elif commit.role == "Volunteer":
                people_rows[name]['volunteer_list'] += str(commit.event)+', '
            elif commit.role in ["Teacher", "Moderator", "Panelist"]:
                people_rows[name]['class_list'] += (
                    commit.role + ': ' + str(commit.event) + ', ')
            elif commit.role == "Performer" and (
                    "General" in commit.event.labels):
                people_rows[name]['show_list'] += str(commit.event)+', '
            
            if commit.people.class_name == "Bio":
                bio = Bio.objects.get(pk=commit.people.class_id)
                if str(bio) not in people_rows[name]['personae_list']:
                    people_rows[name]['personae_list'] += str(bio) + ', '


    for ticket in Transaction.objects.filter(
            ticket_item__ticketing_event__conference=conference,
            purchaser__matched_to_user__is_active=True).exclude(
            purchaser__matched_to_user__username="limbo"):
        name = ticket.purchaser.matched_to_user.profile.get_badge_name(
            ).encode('utf-8').strip()
        if name not in people_rows.keys():
            people_rows[name] = {
                'first': ticket.purchaser.matched_to_user.first_name.encode(
                    'utf-8').strip(),
                'last': ticket.purchaser.matched_to_user.last_name.encode(
                    'utf-8').strip(),
                'ticket_names': "",
                'staff_lead_list': "",
                'volunteer_list': "",
                'class_list': "",
                'personae_list': "",
                'show_list': "",
            }
        people_rows[name]['ticket_names'] += ticket.ticket_item.title + ", "


    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=env_stuff.csv'
    writer = csv.writer(response)
    writer.writerow(header)
    for name, details in people_rows.items():
        writer.writerow([
            name,
            details['first'],
            details['last'],
            details['ticket_names'],
            details['personae_list'],
            details['staff_lead_list'],
            details['volunteer_list'],
            details['class_list'],
            details['show_list']])
    return response


@never_cache
def room_schedule(request, room_id=None):
    viewer_profile = validate_perms(request,
                                    'any',
                                    require=True)

    conference_slugs = Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()

    if room_id:
        rooms = [get_object_or_404(Room, resourceitem_id=room_id)]
    else:
        rooms = Room.objects.filter(conferences=conference)

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            print(booking)
            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():

                if current_day in conf_days:
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'events': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            response = get_people(event_ids=[booking.pk],
                                  roles=class_roles+privileged_event_roles)
            people_set = []
            for people in response.people:
                print
                people_set += [{
                    "role": people.role,
                    "person": eval(people.public_class).objects.get(
                        pk=people.public_id)}]
            day_events += [{'booking': booking,
                            'people': people_set}]
        if current_day in conf_days:
            room_set += [{'room': room,
                          'date': current_day,
                          'events': day_events}]
    return render(request, 'gbe/report/room_schedule.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})


@never_cache
def room_setup(request):

    conference_slugs = Conference.all_slugs()
    if request.GET and request.GET.get('conf_slug'):
        conference = Conference.by_slug(request.GET['conf_slug'])
    else:
        conference = Conference.current_conf()

    conf_days = conference.conferenceday_set.all()
    tmp_days = []
    for position in range(0, len(conf_days)):
        tmp_days.append(conf_days[position].day)
    conf_days = tmp_days

    viewer_profile = validate_perms(request, 'any', require=True)
    rooms = Room.objects.filter(conferences=conference)

    # rearrange the data into the format of:
    #  - room & date of booking
    #       - list of bookings
    # this lets us have 1 table per day per room
    room_set = []
    for room in rooms:
        day_events = []
        current_day = None
        for booking in room.get_bookings:
            if not current_day:
                current_day = booking.start_time.date()
            if current_day != booking.start_time.date():
                if (current_day in conf_days and len(day_events) > 0):
                    room_set += [{'room': room,
                                  'date': current_day,
                                  'bookings': day_events}]
                current_day = booking.start_time.date()
                day_events = []
            if booking.event_style in class_styles:
                day_events += [{'event': booking,
                                'class': Class.objects.get(
                                    pk=booking.connected_id)}]
        if (current_day in conf_days and len(day_events) > 0):
            room_set += [{'room': room,
                          'date': current_day,
                          'bookings': day_events}]

    return render(request,
                  'gbe/report/room_setup.tmpl',
                  {'room_date': room_set,
                   'conference_slugs': conference_slugs,
                   'conference': conference})
