

class Person(object):
    def __init__(self,
                 booking_id=None,
                 user=None,
                 public_id=None,
                 public_class="Performer",
                 role=None,
                 label=None,
                 worker=None):
        if worker:
            self.role = worker.role
            self.user = worker._item.as_subtype.user_object
            self.public_class = worker._item.as_subtype.__class__.__name__
            self.public_id = worker._item.pk
        else:
            self.user = user
            self.public_id = public_id
            self.role = role
            self.public_class = public_class

        self.booking_id = booking_id
        self.label = label


class Casting(object):
    def __init__(self,
                 booking):
        self.booking_id = booking.pk
        self.role = booking.resource.actresource.role
        self.act = booking.resource.actresource._item


class ScheduleItem(object):
    def __init__(self,
                 user=None,
                 group_id=None,
                 event=None,
                 role=None,
                 label=None,
                 booking_id=None):
        self.user = user
        self.group_id = group_id
        self.role = role
        self.label = label
        self.event = event
        self.booking_id = booking_id


class Answer(object):
    def __init__(self,
                 question=None,
                 value=None):
        self.question = question
        self.value = value


class Warning(object):
    def __init__(self,
                 code=None,
                 user=None,
                 occurrence=None,
                 details=None):
        self.code = code
        self.user = user
        self.occurrence = occurrence
        self.details = details


class Error(object):
    def __init__(self,
                 code=None,
                 details=None):
        self.code = code
        self.details = details


class GeneralResponse(object):
    def __init__(self,
                 warnings=[],
                 errors=[]):
        self.warnings = warnings
        self.errors = errors


class OccurrenceResponse(GeneralResponse):
    def __init__(self,
                 occurrence=None,
                 warnings=[],
                 errors=[]):
        self.occurrence = occurrence
        super(OccurrenceResponse, self).__init__(warnings, errors)


class OccurrencesResponse(GeneralResponse):
    def __init__(self,
                 occurrences=[],
                 warnings=[],
                 errors=[]):
        self.occurrences = occurrences
        super(OccurrencesResponse, self).__init__(warnings, errors)


class PersonResponse(GeneralResponse):
    def __init__(self,
                 booking_id=None,
                 warnings=[],
                 errors=[]):
        self.booking_id = booking_id
        super(PersonResponse, self).__init__(warnings, errors)


class PeopleResponse(GeneralResponse):
    def __init__(self,
                 people=[],
                 warnings=[],
                 errors=[]):
        self.people = people
        super(PeopleResponse, self).__init__(warnings, errors)


class CastingResponse(GeneralResponse):
    def __init__(self,
                 castings=[],
                 warnings=[],
                 errors=[]):
        self.castings = castings
        super(CastingResponse, self).__init__(warnings, errors)


class ScheduleResponse(GeneralResponse):
    def __init__(self,
                 schedule_items=[],
                 warnings=[],
                 errors=[]):
        self.schedule_items = schedule_items
        super(ScheduleResponse, self).__init__(warnings, errors)


class RolesResponse(GeneralResponse):
    def __init__(self,
                 roles=[],
                 warnings=[],
                 errors=[]):
        self.roles = roles
        super(RolesResponse, self).__init__(warnings, errors)


class EvalInfoResponse(GeneralResponse):
    def __init__(self,
                 occurrences=[],
                 questions=[],
                 answers=[],
                 warnings=[],
                 errors=[]):
        self.occurrences = occurrences
        self.questions = questions
        self.answers = answers
        super(EvalInfoResponse, self).__init__(warnings, errors)


class EvalSummaryResponse(GeneralResponse):
    def __init__(self,
                 occurrences=[],
                 questions=[],
                 summaries={},
                 count=None,
                 warnings=[],
                 errors=[]):
        self.occurrences = occurrences
        self.questions = questions
        self.summaries = summaries
        self.count = count

        super(EvalSummaryResponse, self).__init__(warnings, errors)
