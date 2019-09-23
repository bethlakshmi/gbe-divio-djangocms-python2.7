from django import template
from django.conf import settings
from settings import (
    GBE_DATETIME_FORMAT,
    GBE_TIME_FORMAT,
)
from django.utils.formats import date_format

register = template.Library()


@register.inclusion_tag('gbe/tag_templates/mailchimp.tmpl')
def mailchimp():
    if settings.MC_API_KEY == 'TEST':
        return {'have_mc': False}
    return {'mc_api_url': settings.MC_API_URL,
            'mc_api_user': settings.MC_API_USER,
            'mc_api_id': settings.MC_API_ID,
            'have_mc': True,
            }


@register.filter
def display_track_title(title, truncated_length):
    title = title.split('/')[-1]
    if len(title) <= truncated_length:
        return title
    else:
        return title[:truncated_length] + "..."


def build_schedule_context(profile):
    events = profile.volunteer_schedule()
    schedule = [
        {'event': str(event),
         'time': "%s - %s" % (date_format(event.starttime, "GBE_DATETIME_FORMAT"),
                              date_format(event.starttime + event.duration,
                                          "GBE_TIME_FORMAT")),
         'location': str(event.location)}
        for event in events]
    return {'schedule': schedule}


@register.inclusion_tag('gbe/tag_templates/schedule.tmpl')
def volunteer_schedule(profile):
    return build_schedule_context(profile)


@register.inclusion_tag('gbe/tag_templates/schedule_plaintext.tmpl')
def volunteer_schedule_plaintext(profile):
    return build_schedule_context(profile)


@register.inclusion_tag('gbe/tag_templates/warning_html.tmpl')
def list_warnings(warnings):
    return {'warnings': warnings}


@register.inclusion_tag('gbe/tag_templates/warning_plaintext.tmpl')
def list_warnings_plaintext(warnings):
    return {'warnings': warnings}
