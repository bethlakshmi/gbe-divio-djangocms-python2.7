from scheduler.models import (
    EventEvalComment,
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
    WorkerItem,
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

answer_type_to_class = {
    "boolean": EventEvalBoolean,
    "grade": EventEvalGrade,
    "text": EventEvalComment,
}


def set_eval_info(answers, occurrence_id, person):
    response = get_occurrence(occurrence_id)
    new_answers = []
    if len(response.errors) > 0:
        return EvalInfoResponse(errors=response.errors)
    if response.occurrence.starttime > datetime.now() - timedelta(
            hours=settings.EVALUATION_WINDOW):
        return EvalInfoResponse(
            warnings=[Warning(
                code="EVENT_IN_FUTURE",
                details="The event hasn't occurred yet, and can't be rated.",
                occurrence=response.occurrence)],
            occurrences=[response.occurrence])
    answer_giver = WorkerItem.objects.get(pk=person.public_id)
    for submitted_answer in answers:
        new_answer, created = answer_type_to_class[
            submitted_answer.question.answer_type].objects.get_or_create(
            profile=answer_giver,
            event=response.occurrence,
            question=submitted_answer.question,
            defaults={'answer': submitted_answer.value})
        new_answers += [new_answer]
    return EvalInfoResponse(occurrences=[response.occurrence],
                            answers=new_answers)
