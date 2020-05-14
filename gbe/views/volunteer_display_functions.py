from gbe.forms import VolunteerBidForm
from django.forms import CharField
from gbe.views.functions import get_participant_form


def get_volunteer_forms(volunteer):
    formset = []
    volunteerform = VolunteerBidForm(
        instance=volunteer,
        prefix='Volunteer Info')

    for interest in volunteer.volunteerinterest_set.filter(
        rank__gt=0).order_by(
            'interest__interest'):
        volunteerform.fields['interest_id-%s' % interest.pk] = CharField(
            max_length=200,
            help_text=interest.interest.help_text,
            label=interest.interest.interest,
            initial=interest.rank_description)
    return [volunteerform, get_participant_form(volunteer.profile)]


def validate_interests(formset):
    valid_interests = True
    like_one_thing = False
    for interest_form in formset:
        # to avoid the hidden object hunt - the two points of difference
        # are the instance, and the initial value
        if interest_form.is_valid():
            if int(interest_form.cleaned_data.get('rank')) > 1:
                like_one_thing = True
        else:
            valid_interests = False
    return valid_interests, like_one_thing
