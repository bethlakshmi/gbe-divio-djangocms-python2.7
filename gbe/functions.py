from django.utils.safestring import mark_safe
from gbe.models import (
    Class,
    Conference,
    ConferenceDay,
    Profile,
    StaffArea,
    UserMessage,
    Volunteer,
)
from scheduler.idd import get_occurrences
from django.http import Http404
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib import messages
from gbetext import (
    difficulty_options,
    no_login_msg,
    full_login_msg,
)
from gbe_forms_text import difficulty_default_text
from gbe_utils.text import no_profile_msg
import json
import urllib
from settings import GBE_DATETIME_FORMAT
import xml.etree.ElementTree as et
import html
from gbe_logging import logger
import sys


def jsonify(data):
    return json.loads(data.replace("u'", "'").replace("'", '"'))
    # output is [u'a', u'k']


def validate_profile(request, require=False):
    '''
    Return the user profile if any
    '''
    if request.user.is_authenticated:
        try:
            return request.user.profile
        except Profile.DoesNotExist:
            if require:
                raise Http404
    else:
        return None


def validate_perms(request, perms, require=True):
    '''
    Validate that the requesting user has the stated permissions
    Returns profile object if perms exist, False if not
    '''
    permitted_roles = []
    profile = validate_profile(request, require=False)
    if not profile:
        if require:
            raise PermissionDenied
        else:
            return False
    has_perm = validate_perms_by_profile(profile, perms)
    if not has_perm and require:
        raise PermissionDenied
    return has_perm


def validate_perms_by_profile(profile, perms='any'):
    privilege_groups = profile.privilege_groups
    if len(privilege_groups) > 0 and (perms == 'any' or any(
            [perm in privilege_groups for perm in perms])):
        return profile

    dynamic_roles = profile.get_priv_roles()
    if perms == 'any' and len(dynamic_roles) > 0:
        return profile
    elif any([perm in dynamic_roles for perm in perms]):
        return profile
    return False               # or just return false if we're just checking


def check_user_and_redirect(request, this_url, source):
    follow_on = '?next=%s' % this_url
    response = {
        'error_url': None,
        'owner': None,
    }
    if not request.user.is_authenticated:
        user_message = UserMessage.objects.get_or_create(
            view=source,
            code="USER_NOT_LOGGED_IN",
            defaults={
                'summary': "Need Login - %s Bid",
                'description': no_login_msg})
        full_msg = full_login_msg % (
            user_message[0].description,
            reverse('login') + follow_on)
        messages.warning(request, full_msg)
        response['error_url'] = reverse(
            'register', urlconf='gbe.urls') + follow_on
        return response
    response['owner'] = validate_profile(request, require=False)
    if not response['owner'] or not response['owner'].complete:
        user_message = UserMessage.objects.get_or_create(
            view=source,
            code="PROFILE_INCOMPLETE",
            defaults={
                'summary': "%s Profile Incomplete",
                'description': no_profile_msg})
        messages.warning(request, user_message[0].description)
        response['error_url'] = reverse(
            'profile_update', urlconf='gbe.urls') + follow_on
    return response


def get_current_conference():
    return Conference.current_conf()


def get_latest_conference():
    # this is a safer bet if you're using something linked off the special menu
    # will always
    current = Conference.current_conf()
    if current is None:
        current = Conference.objects.all().order_by(
            "-conferenceday__day").first()
    return current


def get_conference_by_slug(slug):
    return Conference.by_slug(slug)


def get_conference_days(conference, open_to_public=None):
    if open_to_public is None or open_to_public is False:
        return conference.conferenceday_set.all()
    else:
        return conference.conferenceday_set.filter(
            open_to_public=True)


def get_conference_day(conference, date):
    return ConferenceDay.objects.get(conference=conference, day=date)


def conference_list():
    return Conference.objects.all().order_by("-conference_slug")


def conference_slugs(current=False):
    return Conference.all_slugs(current)


def make_warning_msg(warning, separator="<br>-", use_user=True):
    message_text = ''
    if warning.details:
        message_text += warning.details
    if warning.user and use_user:
        message_text += '%s Affected user: %s' % (
            separator,
            warning.user.profile.display_name)
    if warning.occurrence:
        message_text += '%s Conflicting booking: %s, Start Time: %s' % (
            separator,
            str(warning.occurrence),
            warning.occurrence.starttime.strftime(GBE_DATETIME_FORMAT))
    return message_text


def get_ticketable_gbe_events(conference_slug=None):
    labels = []
    if conference_slug:
        labels = [conference_slug]
    else:
        labels = Conference.all_slugs(current=True)

    event_set = get_occurrences(
        event_styles=['Drop-In', 'Master', 'Special', 'Show'],
        label_sets=[labels]).occurrences

    return event_set


def check_forum_spam(email):
    from gbe.email.functions import notify_admin_on_error
    activity = "Email Spam Check"
    found_it = False
    try:
        url = "http://api.stopforumspam.org/api?email=%s"
        req = urllib.request.Request(url % email)
        res = urllib.request.urlopen(req)
        xml_tree = et.fromstring(res.read())
        was_seen = html.unescape(xml_tree.find('.//appears').text)
        if was_seen == "yes":
            found_it = True
    except urllib.error.URLError as io_error:
        logger.error('Could not perform email check:  %s' % io_error.reason)
        notify_admin_on_error(
            activity,
            ('Could not perform email check (failed open):  %s calling %s ' +
             'to verify email %s') % (io_error.reason, url, email),
            reverse('register', urlconf='gbe.urls'))
    except:
        logger.error(
            'Could not perform BPT call.  Reason: %s ' % (sys.exc_info()[0]))
        notify_admin_on_error(
            activity,
            ('Could not perform email check (failed open):  %s calling %s ' +
             'to verify email %s') % (sys.exc_info()[0], url, email),
            reverse('register', urlconf='gbe.urls'))
    return found_it


def dynamic_difficulty_options():
    dynamic_difficulty_options = []
    for choice in difficulty_options:
        label_desc, created = UserMessage.objects.get_or_create(
            view="ClassDifficulty",
            code="%s_DIFFICULTY" % choice[0].upper(),
            defaults={
                'summary': "%s Difficulty Description" % choice[0],
                'description': difficulty_default_text[choice[0]]})
        dynamic_difficulty_options += [(
            choice[0],
            mark_safe("<b>%s:</b> %s" % (choice[1],
                                         label_desc.description)))]
    return dynamic_difficulty_options
