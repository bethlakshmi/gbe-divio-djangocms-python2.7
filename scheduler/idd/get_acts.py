from scheduler.models import ResourceAllocation
from scheduler.data_transfer import (
    CastingResponse,
    Casting,
)


def get_acts(occurrence_id):
    castings = []
    bookings = ResourceAllocation.objects.filter(
    	event__pk=occurrence_id).order_by('ordering__order')
    for booking in bookings:
        if booking.resource.as_subtype.__class__.__name__ == "ActResource":
            casting = Casting(booking)
            castings += [casting]
    return CastingResponse(castings=castings)
