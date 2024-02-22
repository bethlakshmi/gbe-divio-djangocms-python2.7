from django.contrib.auth.models import User
from gbe.models import Profile
from ticketing.models import Purchaser


def match_existing_purchasers_using_email():
    '''
    Function goes through all of the purchasers in the system, and if
    the purchasers is currently set to the "limbo" user (indicating
    purchaser is not linked to a real user yet) we attempt
    to match it.

    returns None
    '''

    for purchaser in Purchaser.objects.filter(
            matched_to_user__username='limbo'):
        matched_user = attempt_match_purchaser_to_user(purchaser)
        if matched_user is not None:
            purchaser.matched_to_user = matched_user
            purchaser.save()


def attempt_match_purchaser_to_user(purchaser, tracker_id=None):
    '''
    Function attempts to match a given purchaser to a user in the system, using
    the algorithm agreed upon by Betty and Scratch.

    purchaser - the purchaser object to attempt match with
    tracker_id - the tracker ID returned from Brown paper tickets
    returns:  a user id (as an integer) that matched, or -1 if none
    '''

    # First try to match the tracker id to a user in the system
    if tracker_id is not None and isinstance(tracker_id, int):
        user_id = int(tracker_id[3:])
        return User.objects.get(id=user_id)

    # Next try to match to a purchase email address from the Profile
    # (Manual Override Mechanism)

    for profile in Profile.objects.filter(
            purchase_email__iexact=purchaser.email):
        return profile.user_object

    # Finally, try to match to the user's email.  If an overriding
    # purchase_email from the Profile exists for a given user, ignore
    # the user email field for that user.

    for user in User.objects.filter(email__iexact=purchaser.email):
        if not hasattr(
                user,
                'profile') or user.profile.purchase_email is None or len(
                user.profile.purchase_email) == 0:
            return user
    return None
