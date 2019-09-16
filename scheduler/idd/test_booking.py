from scheduler.models import (
    ResourceAllocation,
)


def test_booking(booking_id, occurrence_id):
    return ResourceAllocation.objects.filter(
        pk=booking_id,
        event__pk=occurrence_id).exists()
