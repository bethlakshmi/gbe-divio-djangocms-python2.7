from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import PermissionDenied
from gbe.views import LandingPageView
from gbe.models import (
    Act,
    Class,
    UserMessage,
    Vendor,
)
from gbetext import default_clone_msg


@login_required
def CloneBidView(request, bid_type, bid_id):
    '''
    "Revive" an existing bid for use in the existing conference
    '''
    if bid_type not in ('Act', 'Class', 'Vendor'):
        raise Http404   # or something
    bid = eval(bid_type).objects.get(pk=bid_id)
    if request.user.profile not in bid.profiles:
        raise PermissionDenied
    new_bid = bid.clone()
    user_message = UserMessage.objects.get_or_create(
        view='CloneBidView',
        code="CLONE_%s_SUCCESS" % bid_type.upper(),
        defaults={
            'summary': "Clone %s Success" % bid_type,
            'description': default_clone_msg})
    messages.success(request, user_message[0].description)
    return LandingPageView(request)
