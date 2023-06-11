from scheduler.models import (
    PeopleAllocation,
)


def test_booking(booking_id, occurrence_id):
    return PeopleAllocation.objects.filter(
        pk=booking_id,
        event__pk=occurrence_id).exists()
