from settings import (
    GBE_DATE_FORMAT,
    GBE_DATETIME_FORMAT,
    GBE_TIME_FORMAT,
)
from django.contrib.auth.models import User
from django.conf import settings
from post_office import mail
from post_office.models import EmailTemplate
import os
from django.contrib.sites.models import Site
from django.urls import reverse
from gbe.models import (
    Conference,
    EmailTemplateSender,
    StaffArea,
)
from gbe.functions import make_warning_msg
from gbetext import (
    acceptance_states,
    email_template_desc,
    unique_email_templates,
)
from gbe_utils.text import no_profile_msg
from scheduler.idd import (
    get_all_container_bookings,
    get_occurrences,
)
from django.core.signing import (
    TimestampSigner,
    BadSignature,
    SignatureExpired,
)


def mail_send_gbe(to_list,
                  from_address,
                  template,
                  context,
                  priority='now',
                  from_name=None):
    if settings.DEBUG:
        print("Original To List:")
        print(to_list)
        to_list = []
        for admin in settings.ADMINS:
            to_list += [admin[1]]
    from_complete = settings.DEFAULT_FROM_EMAIL
    reply_to = from_address
    if from_name is not None:
        from_complete = "%s <%s>" % (from_name, settings.DEFAULT_FROM_EMAIL)
        reply_to = "%s <%s>" % (from_name, from_address)
    try:
        mail.send(to_list,
                  from_complete,
                  template=template,
                  context=context,
                  priority=priority,
                  headers={'Reply-to': reply_to},
                  )
    except:
        return "EMAIL_SEND_ERROR"


def send_user_contact_email(name, from_address, message):
    subject = "EMAIL FROM GBE SITE USER %s" % name
    to_addresses = settings.USER_CONTACT_RECIPIENT_ADDRESSES
    mail.send(to_addresses,
              from_address,
              subject=subject,
              message=message,
              priority='now',
              )
    # TO DO: handle (log) possible exceptions
    # TO DO: log usage of this function
    # TO DO: close the spam hole that this opens up.


def get_mail_content(base):
    with open(
        "%s/gbe/templates/gbe/email/%s.tmpl" % (
            settings.BASE_DIR,
            base), "r") as textfile:
        textcontent = textfile.read()
    with open(
        "%s/gbe/templates/gbe/email/%s_html.tmpl" % (
            settings.BASE_DIR,
            base), "r") as htmlfile:
        htmlcontent = htmlfile.read()
    return (textcontent, htmlcontent)


def get_or_create_template(name, base, subject):
    try:
        template = EmailTemplate.objects.get(name=name)
    except:
        (textcontent, htmlcontent) = get_mail_content(base)
        template = EmailTemplate.objects.create(
            name=name,
            subject=subject,
            content=textcontent,
            html_content=htmlcontent,
            )
        template.save()

    try:
        sender = EmailTemplateSender.objects.get(template=template)
    except:
        sender = EmailTemplateSender.objects.create(
            template=template,
            from_email=settings.DEFAULT_FROM_EMAIL,
            from_name=settings.DEFAULT_FROM_NAME,
        )
        sender.save()

    return template


def send_bid_state_change_mail(
        bid_type,
        email,
        badge_name,
        bid,
        status,
        show=None,
        casting=None):
    site = Site.objects.get_current()
    context = {
        'name': badge_name,
        'badge_name': badge_name,
        'bid_type': bid_type,
        'bid': bid,
        'status': acceptance_states[status][1],
        'site': site.domain,
        'site_name': site.name}
    if casting:
        context['casting'] = casting
    if show:
        name = '%s %s - %s' % (
            bid_type.lower(),
            acceptance_states[status][1].lower(),
            str(show).lower())
        action = 'Your %s has been cast in %s' % (
            bid_type,
            str(show))
        if acceptance_states[status][1].lower() == 'wait list':
            action = 'Your %s has been added to the wait list for %s' % (
                bid_type,
                str(show))
        context['show'] = show
        context['show_link'] = "http://" + site.domain + reverse(
            'detail_view',
            args=[show.pk],
            urlconf='gbe.scheduling.urls')
        context['act_tech_link'] = "http://" + site.domain + reverse(
            'act_tech_wizard',
            args=[bid.pk],
            urlconf='gbe.urls')
    else:
        name = '%s %s' % (bid_type, acceptance_states[status][1].lower())
        action = 'Your %s proposal has changed status to %s' % (
            bid_type,
            acceptance_states[status][1])
    template = get_or_create_template(
        name,
        "default_bid_status_change",
        action)
    return mail_send_gbe(
        email,
        template.sender.from_email,
        template=name,
        context=context,
        from_name=template.sender.from_name)


def send_awaiting_approval_mail(
        bid_type,
        email,
        badge_name,
        occurrences):
    site = Site.objects.get_current()
    context = {
        'name': badge_name,
        'badge_name': badge_name,
        'bid_type': "offer to volunteer",
        'occurrences': occurrences,
        'status': "awaiting approval",
        'site': site.domain,
        'site_name': site.name}
    name = '%s %s' % (bid_type, "awaiting approval")
    action = 'Your %s proposal has changed status to %s' % (
        bid_type,
        "awaiting approval")
    template = get_or_create_template(
        name,
        "default_bid_status_change",
        action)
    return mail_send_gbe(
        email,
        template.sender.from_email,
        template=name,
        context=context,
        from_name=template.sender.from_name)


def send_schedule_update_mail(participant_type, profile):
    if profile.email_allowed('schedule_change_notifications'):
        name = '%s schedule update' % (participant_type.lower())
        template = get_or_create_template(
            name,
            "volunteer_schedule_update",
            "A change has been made to your %s Schedule!" % (
                participant_type))
        return mail_send_gbe(
            profile.contact_email,
            template.sender.from_email,
            template=name,
            context={
                'site': Site.objects.get_current().domain,
                'profile': profile,
                'landing_page_url': "http://%s%s" % (
                    Site.objects.get_current().domain,
                    reverse('home',
                            urlconf='gbe.urls')),
                'landing_page_link': "<a href='http://%s%s'>%s</a>" % (
                    Site.objects.get_current().domain,
                    reverse('home',
                            urlconf='gbe.urls'),
                    "Personal Page"),
                'unsubscribe_link': create_unsubscribe_link(
                    profile.contact_email,
                    "send_schedule_change_notifications")
                },
            from_name=template.sender.from_name)


def send_daily_schedule_mail(schedules, day, slug, email_type):
    name = 'daily schedule'
    template = get_or_create_template(
        name,
        "schedule_letter",
        "Your Schedule for Tomorrow at GBE")

    for user, bookings in list(schedules.items()):
        mail_send_gbe(
            user.profile.contact_email,
            template.sender.from_email,
            template=name,
            context={
                'site': Site.objects.get_current().domain,
                'badge_name': user.profile.get_badge_name(),
                'bookings': bookings,
                'day': day.strftime(GBE_DATE_FORMAT),
                'unsubscribe_link': create_unsubscribe_link(
                    user.profile.contact_email,
                    "send_%s" % email_type)
                },
            priority="medium",
            from_name=template.sender.from_name)


def send_act_tech_reminder(act, email_type):
    name = 'act tech reminder'
    template = get_or_create_template(
        name,
        "act_tech_reminder",
        "Reminder to Finish your Act Tech Info")

    return mail_send_gbe(
        act.performer.contact.contact_email,
        template.sender.from_email,
        template=name,
        context={
            'act': act,
            'name': act.performer.name,
            'act_tech_link': "http://" + Site.objects.get_current(
                ).domain + reverse('act_tech_wizard',
                                   args=[act.pk],
                                   urlconf='gbe.urls'),
            'unsubscribe_link': create_unsubscribe_link(
                act.performer.contact.contact_email,
                "send_%s" % email_type)},
            priority="medium",
            from_name=template.sender.from_name)


def send_unsubscribe_link(user):
    name = 'unsubscribe email'
    template = get_or_create_template(
        name,
        "unsubscribe_email",
        "Unsubscribe from GBE Mail")
    mail_send_gbe(
        user.email,
        template.sender.from_email,
        template=name,
        context={
            'site': Site.objects.get_current().domain,
            'badge_name': user.profile.get_badge_name(),
            'unsubscribe_link': create_unsubscribe_link(
                user.profile.contact_email)},
        priority="medium",
        from_name=template.sender.from_name)


def notify_reviewers_on_bid_change(bidder,
                                   bid,
                                   bid_type,
                                   action,
                                   conference,
                                   group_name,
                                   review_url,
                                   show=None):
    name = '%s %s notification' % (bid_type.lower(), action.lower())
    template = get_or_create_template(
        name,
        "bid_submitted",
        "%s %s Occurred" % (bid_type, action))
    to_list = [user.email for user in
               User.objects.filter(groups__name=group_name, is_active=True)]
    if len(to_list) > 0:
        mail_send_gbe(
            to_list,
            template.sender.from_email,
            template=name,
            context={
                'bidder': bidder,
                'bid': bid,
                'bid_type': bid_type,
                'action': action,
                'conference': conference,
                'group_name': group_name,
                'review_url': "http://" + Site.objects.get_current(
                    ).domain+review_url},
            from_name=template.sender.from_name)


def notify_admin_on_error(activity, error, target_link):
    name = '%s error' % (activity.lower())
    template = get_or_create_template(
        name,
        "admin_error",
        '%s Error' % (activity))
    to_list = [admin[1] for admin in settings.ADMINS]
    if len(to_list) > 0:
        mail_send_gbe(
            to_list,
            template.sender.from_email,
            template=name,
            context={
                'activity': activity,
                'error': error,
                'target_link': target_link},
            from_name=template.sender.from_name)


def send_volunteer_update_to_staff(
        active_user,
        vol_profile,
        occurrences,
        state,
        update_response):
    name = 'volunteer changed schedule'
    template = get_or_create_template(
        name,
        "volunteer_schedule_change",
        "Volunteer Schedule Change")
    to_list = []
    occurrence_ids = []
    labels = []
    set_of_events = []
    for occurrence in occurrences:
        occurrence_ids += [occurrence.pk]
        for label in occurrence.labels:
            labels += [label]
        state_change = state
        if state == "on":
            if occurrence.approval_needed:
                state_change = "Awaiting Approval"
            else:
                state_change = "Volunteered"
        elif state == "off":
            state_change = "Withdrawn"
        set_of_events += [{
            'occurrence': occurrence,
            'start': occurrence.start_time.strftime(GBE_DATETIME_FORMAT),
            'end': occurrence.end_time.strftime(GBE_TIME_FORMAT),
            'state_change': state_change}]
    leads = get_all_container_bookings(
        occurrence_ids=occurrence_ids,
        roles=['Staff Lead', ])
    for lead in leads.people:
        for user in lead.users:
            if user.email not in to_list:
                to_list += [user.email]
    for area in StaffArea.objects.filter(
            conference__conference_slug__in=labels,
            slug__in=labels,
            staff_lead__isnull=False):
        if area.staff_lead.user_object.email not in to_list:
            to_list += [area.staff_lead.user_object.email]

    # only mail to coordinators if there are no staff leads
    if len(to_list) == 0:
        to_list = [user.email for user in User.objects.filter(
            groups__name='Volunteer Coordinator',
            is_active=True)]

    warnings = []
    for warning in warnings:
        if not (state == "Rejected" and warning.code == "SCHEDULE_CONFLICT"):
            warnings += [make_warning_msg(warning, "", False)]
    if len(to_list) > 0:
        return mail_send_gbe(
            to_list,
            template.sender.from_email,
            template=name,
            context={
                'active_profile': active_user,
                'profile': vol_profile,
                'occurrences': set_of_events,
                'error': update_response.errors,
                'warnings': warnings},
            from_name=template.sender.from_name)


def get_user_email_templates(user):
    template_set = []
    for priv in user.get_email_privs():
        template_set += [{
            'name': "%s submission notification" % priv,
            'description': email_template_desc[
                "submission notification"] % priv,
            'category': priv,
            'default_base': "bid_submitted",
            'default_subject': "%s Submission Occurred" % priv, }]
        for state in acceptance_states:
            if priv == "act" and state[1] in ("Wait List", "Accepted"):
                for show in get_occurrences(
                        event_styles=['Show'],
                        label_sets=[Conference.all_slugs(current=True)]
                        ).occurrences:
                    subject = 'Your act has been cast in %s'
                    if state[1] == "Wait List":
                        subject = ('Your act has been added to the wait ' +
                                   'list for %s')
                    template_set += [{
                        'name': "%s %s - %s" % (priv,
                                                state[1].lower(),
                                                show.title.lower()),
                        'description': email_template_desc[
                            "%s %s" % (priv,
                                       state[1].lower())] % show.title,
                        'category': priv,
                        'default_base': "default_bid_status_change",
                        'default_subject': subject % (show.title), }]
            elif priv != "volunteer" and state[1] == 'Awaiting Approval':
                pass
            else:
                template_set += [{
                    'name': "%s %s" % (priv, state[1].lower()),
                    'description': email_template_desc[state[1]] % priv,
                    'category': priv,
                    'default_base': "default_bid_status_change",
                    'default_subject':
                        'Your %s proposal has changed status to %s' % (
                            priv,
                            state[1]), }]
        if priv in unique_email_templates:
            template_set += unique_email_templates[priv]
    if "Scheduling Mavens" in user.privilege_groups:
        template_set += unique_email_templates['scheduling']
    if "Registrar" in user.privilege_groups:
        template_set += unique_email_templates['registrar']
    return sorted(template_set,
                  key=lambda item: (item['name'], item['category']))


def create_unsubscribe_link(email, disable=None):
    token = TimestampSigner().sign(email)
    link = reverse('email_update', urlconf='gbe.urls', args=[token])
    if disable:
        link = link + "?email_disable=" + disable
    return link


def extract_email(token):
    email = None
    try:
        # valid for 30 days
        email = TimestampSigner().unsign(token, max_age=60 * 60 * 24 * 30)
    except (BadSignature, SignatureExpired):
        return False
    return email
