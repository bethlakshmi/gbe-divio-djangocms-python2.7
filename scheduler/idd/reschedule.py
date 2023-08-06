from scheduler.data_transfer import GeneralResponse
from scheduler.models import (
    People,
    PeopleAllocation,
)
from gbetext import not_scheduled_roles


# built for merging, hopefully reuseable on withdrawing
def reschedule(original_public_class,
               original_public_id,
               new_public_class,
               new_public_id):
    sched_items = []

    new_people, created = People.objects.get_or_create(
        class_id=new_public_id,
        class_name=new_public_class)
    new_people.save()

    PeopleAllocation.objects.filter(
        people__class_name=original_public_class,
        people__class_id=original_public_id).update(people=new_people)

    return GeneralResponse()
