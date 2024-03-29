from scheduler.models import People
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def update_bookable_people(public_object,
                           users,
                           commitment_class_name="",
                           commitment_class_id=None):

    people = People.objects.get(
        class_id=public_object.pk,
        class_name=public_object.__class__.__name__,
        commitment_class_name=commitment_class_name,
        commitment_class_id=commitment_class_id)

    people.users.clear()
    for user in users:
        people.users.add(user)
    return PeopleResponse(people=[Person(people=people)])
