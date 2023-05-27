from scheduler.models import People
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookable_people_by_user(user):
    people_set = []
    for people in People.objects.filter(users__pk=user.pk):
        people_set += [Person(people=people)]
    return PeopleResponse(people=people_set)
