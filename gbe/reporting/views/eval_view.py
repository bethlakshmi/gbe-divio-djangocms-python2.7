from django.shortcuts import render
from django.views.decorators.cache import never_cache
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from django.urls import reverse
from scheduler.idd import (
    get_eval_info,
    get_eval_summary,
)
from gbe.models import (
    Bio,
    Conference,
    UserMessage,
)
from settings import GBE_TABLE_FORMAT
from gbetext import eval_report_explain_msg
from gbe.scheduling.views.functions import (
    show_general_status,
)


@never_cache
def eval_view(request, occurrence_id=None):
    details = None
    reviewer = validate_perms(request, ('Class Coordinator', ))
    conference = None
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    if occurrence_id and not conference:
        detail_response = get_eval_info(occurrence_id=int(occurrence_id))
        show_general_status(request, detail_response, "EvaluationDetailView")
        if detail_response.occurrences and len(
                detail_response.occurrences) > 0:
            occurrence = detail_response.occurrences[0]
            detail_response.answers.sort(
                key=lambda answer: (answer.profile.profile.display_name,
                                    answer.question.order))
            details = {
                'occurrence': occurrence,
                'title': occurrence.title,
                'description': occurrence.description,
                'questions': detail_response.questions,
                'evaluations': detail_response.answers,
            }
            if not conference:
                conference = Conference.objects.filter(
                    conference_slug__in=occurrence.labels)[0]
    if not conference:
        conference = get_current_conference()

    response = get_eval_summary(
        labels=[conference.conference_slug, "Conference"])

    display_list = []
    summary_view_data = {}
    for occurrence in response.occurrences:
        teachers = []
        interested = []
        for person in occurrence.people:
            if person.role == "Interested":
                interested += [person]
            elif person.role in ("Teacher", "Moderator"):
                teachers += [Bio.objects.get(pk=person.public_id)]

        display_item = {
            'id': occurrence.id,
            'start':  occurrence.start_time.strftime(GBE_TABLE_FORMAT),
            'title': occurrence.title,
            'teachers': teachers,
            'interested': len(interested),
            'eval_count': response.count.get(occurrence.pk, 0),
            'detail_link': reverse(
                'evaluation_detail',
                urlconf='gbe.reporting.urls',
                args=[occurrence.id])}
        display_list += [display_item]
        summary_view_data[int(occurrence.id)] = {}
    for question in response.questions:
        for item in response.summaries[question.pk]:
            summary_view_data[int(item['event'])][int(question.pk)] = item[
                'summary']

    user_message = UserMessage.objects.get_or_create(
        view="InterestView",
        code="ABOUT_EVAL_REPORT",
        defaults={
            'summary': "About Evaluation Report",
            'description': eval_report_explain_msg})
    return render(request,
                  'gbe/report/evals.tmpl',
                  {'columns': ['Class',
                               'Teacher(s)',
                               'Time',
                               '# Interested',
                               '# Evaluations'],
                   'vertical_columns': response.questions.values_list(
                        'question',
                        flat=True),
                   'last_columns': ['Actions'],
                   'classes': display_list,
                   'questions': response.questions,
                   'summaries': summary_view_data,
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'about': user_message[0].description,
                   'details': details})
