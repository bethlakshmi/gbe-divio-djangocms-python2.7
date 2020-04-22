from datetime import (
    date,
    timedelta,
    time,
    datetime
)
from calendar import timegm
from gbe.duration import Duration
from random import choice
from gbe.functions import (
    get_conference_by_slug,
    get_current_conference_slug,
)
import string
import math
from django.contrib.sites.models import Site
from django.utils.formats import date_format
from django.core.urlresolvers import reverse
import pytz
from scheduler.models import Location
from gbe.functions import get_gbe_schedulable_items

utc = pytz.timezone('UTC')


def event_info(confitem_type='Show',
               filter_type=None,
               cal_times=(datetime(2016, 2, 5, 18, 0,
                                   tzinfo=pytz.timezone('UTC')),
                          datetime(2016, 2, 7, 0, 0,
                                   tzinfo=pytz.timezone('UTC'))),
               conference=None):
    '''
    Using the scheduleable items for the current conference, get a list
    of dicts for the dates selected
    '''
    confitems_list = get_gbe_schedulable_items(
        confitem_type,
        filter_type,
        conference)

    confitems_list = [confitem for confitem in confitems_list if
                      confitem.schedule_ready and confitem.visible]

    loc_allocs = []
    for l in Location.objects.all():
        loc_allocs += l.allocations.all()

    scheduled_events = []
    scheduled_event_ids = []
    for alloc in loc_allocs:
        start_t = utc.localize(alloc.event.start_time)
        stop_t = utc.localize(alloc.event.start_time + alloc.event.duration)
        if start_t < cal_times[1] and stop_t >= cal_times[0]:
            scheduled_events += [alloc.event]
            scheduled_event_ids += [alloc.event.eventitem_id]

    events_dict = {}
    for index in range(len(scheduled_event_ids)):
        for confitem in confitems_list:
            if scheduled_event_ids[index] == confitem.eventitem_id:
                events_dict[scheduled_events[index]] = confitem

    events = [{'title': confitem.e_title,
               'link': reverse('detail_view', urlconf='gbe.scheduling.urls',
                               args=[str(confitem.eventitem_id)]),
               'description': confitem.e_description,
               'start_time': event.start_time,
               'stop_time': event.start_time + confitem.duration,
               'location': event.location.room.name,
               'type': "%s.%s" % (
                   event.event_type_name,
                   event.confitem.type)}
              for (event, confitem) in list(events_dict.items())]
    return events


def select_day(days, day_name):
    '''
    Take a list of conference_days, return the one whose name is day_name
    Behavior is undefined if conference has more than one instance of a
    given day of week. This is a bug.
    '''
    return {d.day.strftime("%A"): d for d in days}.get(day_name, None)


def date_to_datetime(the_date):
    zero_hour = time(0)
    return utc.localize(datetime.combine(the_date, zero_hour))


def get_default_range():
    today = date_to_datetime(date.today())
    return (today + Duration(hours=8), today + Duration(hours=28))


def cal_times_for_conf(conference, day_name=None):
    from gbe.functions import get_conference_days  # late import, circularity
    days = get_conference_days(conference)

    if not days.exists():
        return get_default_range()
    if day_name:
        selected_day = select_day(days, day_name)
        if not selected_day:
            return get_default_range()
        day = date_to_datetime(selected_day.day)
        if day:
            return day + Duration(hours=8), day + Duration(hours=28)

    else:
        first_day = date_to_datetime(days.first().day)
        last_day = date_to_datetime(days.last().day)
        return (first_day + Duration(hours=8), last_day + Duration(hours=28))


def calendar_export(conference=None,
                    cal_format='gbook',
                    event_types='All',
                    day=None,
                    ):
    '''
    View to export calendars, formatted in either iCalendar format, or as
    a csv file.  Used to allow importing of the calendar information into
    other applications, such as Guidebook, or Calendar applications.

    conference  - Slug for the conference we want to export data for
    cal_format  - Which format to use for the exported data, can be 'gbook'
                  for Guidebook csv, 'ical' for iCal calendar programs (ics)
    event_types - Which event types to include, usually will be 'All' to
                  generate a complete calendar, but could also be 'Class',
                  'Show', etc, or a list or tuple of event_types
    day         - Which day of the conference to get calendar info for,
                  None or 'All' gets info for entire conference
    '''
    #  TODO: Add ability to filter on a users schedule for things like
    #  volunteer shifts.

    url = 'http://'  # Want to find this through Site or similar
    site = Site.objects.get_current().domain

    if conference is None:
        conference = get_current_conference_slug()
    else:
        conference = get_conference_by_slug(conference)

    if day == 'All':
        day = None
    cal_times = cal_times_for_conf(conference, day)

    if event_types == 'All' or event_types == 'All':
        event_types = ['Show',
                       'Class',
                       'Special Event',
                       'Master',
                       'Drop-In',
                       ]
    if event_types == 'Show' or event_types == 'Show':
        event_types == ['Show',
                        'Special Event',
                        'Master',
                        'Drop-In',
                        ]
    if type(event_types) in (type(''), type('')):
        event_types = [event_types]
    events = []
    for event_type in event_types:
        events = events + event_info(confitem_type=event_type,
                                     cal_times=cal_times,
                                     conference=conference)
    if cal_format == 'gbook':
        line_misc = ''
        line_end = '\r\n'

        # Guidebook's allowed fields are:
        # Session Title, Date, Time Start, Time End, Room/Location,
        # Schedule Track (Optional), Description (Optional),
        # Allow Checkin (Optional), Checkin Begin (Optional),
        # Limit Spaces? (Optional), Allow Waitlist (Optional)
        return_file = '"Session Title",' + \
                      '"Date",' + \
                      '"Time Start",' + \
                      '"Time End",' + \
                      '"Room/Location",' + \
                      '"Schedule Track (Optional)",' + \
                      '"Description (Optional)",' + \
                      '"Link To URL ID (Optional)",' + \
                      '"Link To URL Name (Optional)"' + line_end

        for event in events:
            title = event['title'].replace('\n', '') \
                 .replace('\r', '') \
                 .replace('"', '') \
                 .replace("'", '`')
            csv_line = '"%s",' % (title)
            csv_line = csv_line + '"%s",' % \
                (date_format(event['start_time'], 'DATE_FORMAT')
                 .replace(',', ''))
            csv_line = csv_line + '"%s",' % \
                (date_format(event['start_time'], 'TIME_FORMAT')
                 .replace('a.m.', 'AM').replace('p.m.', 'PM')
                 .replace('am', 'AM').replace('pm', 'PM')
                 .replace('noon', '12 PM').replace('midnight', '12 AM'))
            csv_line = csv_line + '"%s",' % \
                (date_format(event['stop_time'], 'TIME_FORMAT')
                 .replace('a.m.', 'AM').replace('p.m.', 'PM')
                 .replace('am', 'AM').replace('pm', 'PM')
                 .replace('noon', '12 PM').replace('midnight', '12 AM'))
            csv_line = csv_line + '"%s",' % (event['location'])
            first_type, second_type = event['type'].split('.')
            if first_type == "GenericEvent":
                csv_line = csv_line + '"%s",' % (second_type)
            else:
                csv_line = csv_line + '"%s",' % (first_type)
            description = event['description'].replace('\n', '') \
                                              .replace('\r', '') \
                                              .replace('"', '') \
                                              .replace("'", '`')
            csv_line = csv_line + '"%s",' % description
            csv_line = csv_line + '"%s%s",' % (url+site, event['link'])
            csv_line = csv_line + '"%s",' % (title)
            csv_line = csv_line + line_misc + line_end

            return_file = return_file + csv_line

    elif cal_format == 'ical':
        return_file = '''
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Great Burlesque Exposition//GBE2 Scheduler//EN
'''
        for event in events:
            return_file = return_file + 'BEGIN:VEVENT\n'
            return_file = return_file + 'UID:%s-%s-%s@%s\n' \
                % (conference.conference_slug,
                   event['title'].replace(' ', ''),
                   event['start_time'].strftime('%F-%R'),
                   site.replace('www.', '')
                   )
            return_file = return_file + 'DTSTAMP:%s\n' % \
                (event['start_time'].strftime('%Y%m%dT%H%M%SZ'))
            return_file = return_file + 'TZID:%s\n' % \
                (event['start_time'].strftime('%Z'))
            return_file = return_file + 'DTSTART:%s\n' % \
                (event['start_time'].strftime('%Y%m%dT%H%M%SZ'))
            return_file = return_file + 'DTEND:%s\n' % \
                (event['stop_time'].strftime('%Y%m%dT%H%M%SZ'))
            return_file = return_file + 'SUMMARY:%s\n' % \
                (event['title'])
            return_file = return_file + 'URL:%s%s\n' % \
                (url+site, event['link'])
            return_file = return_file + 'END:VEVENT\n'
        return_file = return_file + 'END:VCALENDAR\n'

    return return_file


def get_scheduled_events_by_role(conference, roles):
    '''
    gets all the workeritems scheduled with a given set of roles for the
    given conference
    '''
    from scheduler.models import (
        ResourceAllocation,
        Worker,
    )
    commits = ResourceAllocation.objects.filter(
        event__eventitem__event__e_conference=conference)
    workers = Worker.objects.filter(role__in=roles)
    return workers, commits
