from scheduler.models import People
from scheduler.data_transfer import (
    PeopleResponse,
    Person,
)


def get_bookable_people(public_id,
                        public_class,
                        commitment_class_name="",
                        commitment_class_id=None):
    # rigidly checks to get unique person (including commitment) unless 
    # "any" is specified for commitment_class_id, in which case it gets
    # ALL commitments for this public identity.
    people_set = []
    people_filter = People.objects.filter(class_id=public_id,
                                          class_name=public_class)
    if commitment_class_id != "any":
        people_filter = people_filter.filter(
            commitment_class_id=commitment_class_id,
            commitment_class_name=commitment_class_name)
    for item in people_filter:
        people_set += [Person(people=item)]
    return PeopleResponse(people=people_set)
