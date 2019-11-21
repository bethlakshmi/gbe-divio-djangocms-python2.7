from gbe.models import ConferenceDay
from scheduler.idd import get_schedule
from datetime import (
    date,
    datetime,
    time,
    timedelta,
)
import pytz
from gbe.email.functions import send_daily_schedule_mail


def schedule_email():
    personal_schedules = {}
    boston_today = datetime.now().date()
    target_day = boston_today + timedelta(days=1)
    try:
        conf_day = ConferenceDay.objects.get(day=target_day)
    except ConferenceDay.DoesNotExist:
        return 0
    sched_resp = get_schedule(
        start_time=datetime.combine(
            target_day,
            time(0, 0, 0, 0)),
        end_time=datetime.combine(
                target_day+timedelta(days=1),
                time(0, 0, 0, 0)))
    for item in sched_resp.schedule_items:
        if item.user.profile.email_allowed('daily_schedule'):
            if item.user in personal_schedules:
                personal_schedules[item.user] += [item]
            else:
                personal_schedules[item.user] = [item]
    send_daily_schedule_mail(
        personal_schedules,
        target_day,
        conf_day.conference.conference_slug)
    return len(personal_schedules)
