from scheduler.models import People
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def create_bookable_people(public_object, users):
    people = People(class_id=public_object.pk,
                    class_name=public_object.__class__.__name__)
    people.save()
    for user in users:
        people.users.add(user)
    return PeopleResponse(people=[Person(people=people)])
