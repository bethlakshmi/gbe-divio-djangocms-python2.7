from scheduler.idd import get_occurrence


def set_person(occurrence_id,
               person):
    occ_response = get_occurrence(occurrence_id)
    if occ_response.errors:
        return occ_response

    return occ_response.occurrence.allocate_person(person)
