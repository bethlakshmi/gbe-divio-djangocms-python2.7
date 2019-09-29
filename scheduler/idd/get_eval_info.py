from scheduler.models import (
    EventEvalComment,
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
)
from scheduler.data_transfer import (
    EvalInfoResponse,
    Warning,
)
from scheduler.idd import get_occurrence
from datetime import (
    datetime,
    timedelta,
)
import pytz
from django.conf import settings


def get_eval_info(occurrence_id=None, person=None, visible=True):
    occurrences = []
    if occurrence_id:
        response = get_occurrence(occurrence_id)
        if len(response.errors) > 0:
            return EvalInfoResponse(errors=response.errors)
        occurrences += [response.occurrence]
        if response.occurrence.starttime > (datetime.now() - timedelta(
                hours=settings.EVALUATION_WINDOW)):
            return EvalInfoResponse(
                warnings=[Warning(
                    code="EVENT_IN_FUTURE",
                    details="The event hasn't occurred yet, " +
                            "and can't be rated.",
                    occurrence=response.occurrence)],
                occurrences=occurrences)
    if visible:
        questions = EventEvalQuestion.objects.filter(visible=visible)
    else:
        questions = EventEvalQuestion.objects.all()

    answers = []
    for eval_type in [EventEvalComment, EventEvalGrade, EventEvalBoolean]:
        some_answers = eval_type.objects.filter(question__in=questions)
        if occurrence_id:
            some_answers = some_answers.filter(event__in=occurrences)
        if person:
            some_answers = some_answers.filter(profile__pk=person.public_id)
        answers += list(some_answers.order_by('profile__profile__display_name',
                                              'question__order'))
    if len(occurrences) == 0:
        for answer in answers:
            if answer.event not in occurrences:
                occurrences += [answer.event]
    return EvalInfoResponse(occurrences=occurrences,
                            questions=questions,
                            answers=answers)
