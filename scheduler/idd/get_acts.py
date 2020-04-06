from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    CastingResponse,
    Casting,
    Error,
)


def get_acts(occurrence_id=None, foreign_event_ids=[]):
    castings = []
    if occurrence_id:
        bookings = ResourceAllocation.objects.filter(
            event__pk=occurrence_id).order_by('ordering__order')
    elif len(foreign_event_ids) > 0:
        bookings = ResourceAllocation.objects.filter(
            event__eventitem__eventitem_id__in=foreign_event_ids
            ).order_by('ordering__order')
    else:
        return CastingResponse(errors=[Error(
            code="INVALID_REQUEST",
            details="either occurrence_id or foreign_event_ids is required")])
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "ActResource":
            casting = Casting(booking)
            castings += [casting]
    return CastingResponse(castings=castings)
