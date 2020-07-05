from gbe.models import (
    Class,
    Conference,
    ConferenceDay,
    Event,
    GenericEvent,
    Profile,
    Show,
    StaffArea,
    UserMessage,
    Volunteer,
)
from django.http import Http404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib import messages
from gbetext import (
    no_profile_msg,
    no_login_msg,
    full_login_msg,
)
import json
from settings import GBE_DATETIME_FORMAT
from django.db.models import Q


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
    event_roles = ['Technical Director', 'Producer', 'Staff Lead']

    if not profile:
        if require:
            raise PermissionDenied
        else:
            return False
    if perms == 'any':
        if len(profile.privilege_groups) > 0 or any(
                [perm in profile.get_roles() for perm in event_roles]):
            return profile
        else:
            if require:
                raise PermissionDenied
            else:
                return False
    if any([perm in profile.privilege_groups for perm in perms]):
        return profile
    if any([perm in profile.get_roles() for perm in perms]):
        return profile
    if require:                # error out if permission is required
        raise PermissionDenied
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
            reverse('login', urlconf='gbe.urls') + follow_on)
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
            'register', urlconf='gbe.urls') + follow_on
    return response


def get_conf(biddable):
    conference = biddable.biddable_ptr.b_conference
    old_bid = conference.status == 'completed'
    return conference, old_bid


def get_current_conference():
    return Conference.current_conf()


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
    return Conference.objects.all()


def conference_slugs():
    return Conference.all_slugs()


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
    shows = Show.objects.all()
    genericevents = GenericEvent.objects.filter(
        type__in=('Drop-In', 'Master', 'Special'))
    event_set = Event.objects.filter(
        Q(show__in=shows) |
        Q(genericevent__in=genericevents))
    if conference_slug:
        return event_set.filter(e_conference__conference_slug=conference_slug)
    else:
        return event_set.exclude(e_conference__status="completed")
