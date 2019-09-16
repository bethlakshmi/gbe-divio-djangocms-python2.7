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

    questions = base.exclude(answer_type="text").order_by(
        'order')

    for question in questions:
        summary = None
        if question.answer_type == "boolean":
            summary = EventEvalBoolean.objects.filter(
                event__in=response.occurrences,
                question=question).values(
                'event').annotate(
                summary=Avg('answer'))
        if question.answer_type == "grade":
            summary = EventEvalGrade.objects.filter(
                event__in=response.occurrences,
                question=question).values(
                'event').annotate(
                summary=Avg('answer'))
        summaries[question.pk] = summary

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
