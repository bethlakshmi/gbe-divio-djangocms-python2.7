

class Commitment(object):
    def __init__(self,
                 role=None,
                 decorator_class=None,
                 order=None,
                 ordering=None):
        self.class_id = None
        self.class_name = ""

        if ordering is not None:
            o = ordering
            self.class_id = o.people_allocated.people.commitment_class_id
            self.class_name = o.people_allocated.people.commitment_class_name
            self.role = o.role
            self.people_allocated = o.people_allocated
            self.order = o.order
        else:
            if decorator_class:
                self.class_name = decorator_class.__class__.__name__
                self.class_id = decorator_class.pk
            self.role = role
            self.order = order


class Person(object):
    def __init__(self,
                 booking_id=None,
                 public_id=None,
                 public_class="Performer",
                 role=None,
                 label=None,
                 people=None,
                 booking=None,
                 commitment=None,
                 users=None):
        self.booking_id = None
        self.commitment = commitment
        self.users = None
        self.label = None

        if booking:
            self.booking_id = booking.pk
            self.occurrence = booking.event
            self.role = booking.role
            self.label = booking.label
            people = booking.people
            if hasattr(booking, 'ordering'):
                self.commitment = Commitment(ordering=booking.ordering)
        else:
            self.occurrence = None

        if people:
            self.users = people.users.all()
            self.public_class = people.class_name
            self.public_id = people.class_id
            if self.commitment is None:
                self.commitment = Commitment()
                self.commitment.class_id = people.commitment_class_id
                self.commitment.class_name = people.commitment_class_name
        else:
            self.users = users
            self.public_id = public_id
            self.public_class = public_class

        if role:
            self.role = role
        if booking_id:
            self.booking_id = booking_id
        if label:
            self.label = label

        if self.users is None:
            self.users = users
        if self.commitment is None:
            self.commitment = Commitment()


class ScheduleItem(object):
    def __init__(self,
                 user=None,
                 group_id=None,
                 event=None,
                 role=None,
                 label=None,
                 booking_id=None,
                 order=None):
        self.user = user
        self.group_id = group_id
        self.role = role
        self.label = label
        self.event = event
        self.booking_id = booking_id
        self.commitment = None
        if order is not None:
            self.commitment = Commitment(ordering=order)


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


class BookingResponse(GeneralResponse):
    booking_ids = []
    occurrences = []

    def __init__(self,
                 booking_id=None,
                 occurrence=None,
                 warnings=[],
                 errors=[]):
        if booking_id:
            self.booking_ids = [booking_id]
        if occurrence:
            self.occurrences = [occurrence]
        super(BookingResponse, self).__init__(warnings, errors)


class PeopleResponse(GeneralResponse):
    def __init__(self,
                 people=[],
                 warnings=[],
                 errors=[]):
        self.people = people
        super(PeopleResponse, self).__init__(warnings, errors)


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
