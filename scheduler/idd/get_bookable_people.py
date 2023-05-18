from scheduler.models import People
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookable_people(public_id, public_class):
    people = []
    if People.objects.filter(class_id=public_id,
                             class_name=public_class).exists():
        people += [Person(people=People.objects.get(class_id=public_id,
                                                    class_name=public_class))]
    return PeopleResponse(people=people)
