from gbe.functions import get_current_conference
from gbe.email.functions import send_sign_form_reminder
from gbe.ticketing_idd_interface import get_signatories


def sign_form_reminder():
    email_type = 'schedule_change_notifications'
    reminders_sent = 0
    conference = get_current_conference()
 
    for user, forms in get_signatories(conference).items():
        send_sign_form_reminder(user, conference, email_type)
        reminders_sent = reminders_sent + 1
    return reminders_sent
