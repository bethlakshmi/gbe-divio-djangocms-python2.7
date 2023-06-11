from scheduler.models import People
from scheduler.data_transfer import (
    Error,
    GeneralResponse
)


def delete_bookable_people(public_object):
    response = GeneralResponse()
    if not People.objects.filter(class_name=public_object.__class__.__name__,
                                 class_id=public_object.pk).exists():
        response.errors = [Error(
            code="PEOPLE_NOT_FOUND",
            details="People linked to this object were not found: %s - %d" % (
                public_object.__class__.__name__,
                public_object.pk)), ]
    else:
        People.objects.filter(class_name=public_object.__class__.__name__,
                              class_id=public_object.pk).delete()

    return response
