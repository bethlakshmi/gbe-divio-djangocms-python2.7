from gbe.models import (
    EmailTemplateSender,
)

from django.contrib.auth.models import User
from django.conf import settings
from post_office import mail
from post_office.models import EmailTemplate
import os
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
#from gbe.models import Show
from gbetext import (
    acceptance_states,
    email_template_desc,
    no_profile_msg,
    unique_email_templates,
)


def mail_send_gbe(to_list,
                  from_address,
                  template,
                  context,
                  priority='now'):
    if settings.DEBUG:
        to_list = []
        for admin in settings.ADMINS:
            to_list += [admin[1]]

    try:
        mail.send(to_list,
                  from_address,
                  template=template,
                  context=context,
                  priority=priority,
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
            from_email=settings.DEFAULT_FROM_EMAIL
        )
        sender.save()

    return template

def send_bid_state_change_mail(
        bid_type,
        email,
        badge_name,
        bid,
        status,
        show=None):
    site = Site.objects.get_current()
    context = {
        'name': badge_name,
        'bid_type': bid_type,
        'bid': bid,
        'status': acceptance_states[status][1],
        'site': site.domain,
        'site_name': site.name}
    if show:
        name = '%s %s - %s' % (
            bid_type.lower(),
            acceptance_states[status][1].lower(),
            str(show).lower())
        action = 'Your %s has been cast in %s' % (
            bid_type,
            str(show))
        context['show'] = show
        context['show_link'] = site.domain + reverse(
            'detail_view',
            args=[show.pk],
            urlconf='gbe.scheduling.urls')
        context['act_tech_link'] = site.domain + reverse(
            'act_techinfo_edit',
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
        context=context)


def send_schedule_update_mail(participant_type, profile):
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
            'landing_page_link': "<a href='http://%s%s'>Personal Page</a>" % (
                Site.objects.get_current().domain,
                reverse('home',
                        urlconf='gbe.urls'))},
    )


def send_daily_schedule_mail(schedules, day, slug):
    name = 'daily schedule'
    template = get_or_create_template(
        name,
        "schedule_letter",
        "Your Schedule for Tomorrow at GBE")
    for user, bookings in schedules.items():
        mail_send_gbe(
            user.profile.contact_email,
            template.sender.from_email,
            template=name,
            context={
                'site': Site.objects.get_current().domain,
                'badge_name': user.profile.get_badge_name(),
                'bookings': bookings,
                'day': day.strftime(settings.DATE_FORMAT)},
            priority="medium")


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
                'review_url': Site.objects.get_current().domain+review_url},
            )


def send_warnings_to_staff(bidder,
                           bid_type,
                           warnings):
    name = '%s schedule warning' % (bid_type.lower())
    template = get_or_create_template(
        name,
        "schedule_conflict",
        "URGENT: %s Schedule Conflict Occurred" % (bid_type))
    to_list = [user.email for user in
               User.objects.filter(groups__name='%s Coordinator' % bid_type,
                                   is_active=True)]
    for warning in warnings:
        if 'email' in warning:
            to_list += [warning['email']]
    if len(to_list) > 0:
        mail_send_gbe(
            to_list,
            template.sender.from_email,
            template=name,
            context={
                'bidder': bidder,
                'bid_type': bid_type,
                'warnings': warnings},
            )


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
            if priv == "act" and state[1] == "Accepted":
                for show in Show.objects.filter(
                        e_conference__status__in=('upcoming', 'ongoing')):
                    template_set += [{
                        'name': "%s %s - %s" % (priv,
                                                state[1].lower(),
                                                show.e_title.lower()),
                        'description': email_template_desc[
                            "%s %s" % (priv,
                                       state[1].lower())] % show.e_title,
                        'category': priv,
                        'default_base': "default_bid_status_change",
                        'default_subject': 'Your act has been cast in %s' % (
                            show.e_title), }]
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
    return sorted(template_set,
                  key=lambda item: (item['name'], item['category']))
