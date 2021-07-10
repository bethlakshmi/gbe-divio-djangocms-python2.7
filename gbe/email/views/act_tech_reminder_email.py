from gbe.models import Act
from gbe.email.functions import send_act_tech_reminder


def act_tech_reminder():
    email_type = 'schedule_change_notifications'
    reminders_sent = 0
    for act in Act.objects.filter(
            b_conference__status__in=["upcoming", "ongoing"],
            performer__contact__preferences__send_schedule_change_notifications=True):
        if not act.is_complete:
            send_act_tech_reminder(act, email_type)
            reminders_sent = reminders_sent + 1
    return reminders_sent
