from scheduler.models import (
    EventEvalComment,
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
)
from scheduler.data_transfer import (
    EvalSummaryResponse,
)
from scheduler.idd import get_occurrences
from datetime import (
    datetime,
    timedelta,
)
import pytz
from django.conf import settings
from django.db.models import Count, Avg


def get_eval_summary(labels, visible=True):
    summaries = {}
    response = get_occurrences(labels=labels)

    if visible:
        base = EventEvalQuestion.objects.filter(visible=visible)
    else:
        base = EventEvalQuestion.objects.all()

    questions = base.filter(answer_type="grade").order_by(
        'order')

    for question in questions:
        summaries[question.pk] = EventEvalGrade.objects.filter(
                event__in=response.occurrences,
                question=question).values(
                'event').annotate(
                summary=Avg('answer'))

    count_question = EventEvalQuestion.objects.filter(
        visible=True,
        answer_type="grade").first()
    count = {}
    for item in EventEvalGrade.objects.filter(
            event__in=response.occurrences,
            question=count_question).values('event').annotate(
            eval_count=Count('event')):
        count[item['event']] = item['eval_count']
    return EvalSummaryResponse(occurrences=response.occurrences,
                               questions=questions,
                               summaries=summaries,
                               count=count)
