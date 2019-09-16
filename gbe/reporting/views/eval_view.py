from django.shortcuts import render
from django.views.decorators.cache import never_cache
from gbe.functions import (
    conference_slugs,
    get_current_conference,
    get_conference_by_slug,
    validate_perms,
)
from django.core.urlresolvers import reverse
from scheduler.idd import (
    get_eval_info,
    get_eval_summary,
)
from gbe.models import (
    Class,
    Performer,
    UserMessage,
)
from expo.settings import (
    DATE_FORMAT,
    DATETIME_FORMAT,
    TIME_FORMAT,
    URL_DATE,
)
from gbetext import eval_report_explain_msg
from gbe.scheduling.views.functions import (
    show_general_status,
)


@never_cache
def eval_view(request, occurrence_id=None):
    details = None
    reviewer = validate_perms(request, ('Class Coordinator', ))
    if request.GET and request.GET.get('conf_slug'):
        conference = get_conference_by_slug(request.GET['conf_slug'])
    else:
        conference = get_current_conference()
    if occurrence_id:
        detail_response = get_eval_info(occurrence_id=int(occurrence_id))
        show_general_status(request, detail_response, "EvaluationDetailView")
        if detail_response.occurrences and len(
                detail_response.occurrences) > 0:
            detail_response.answers.sort(
                key=lambda answer: (answer.profile.profile.display_name,
                                    answer.question.order))
            details = {
                'occurrence': detail_response.occurrences[0],
                'title': detail_response.occurrences[
                    0].eventitem.event.e_title,
                'description': detail_response.occurrences[
                    0].eventitem.event.e_description,
                'questions': detail_response.questions,
                'evaluations': detail_response.answers,
            }

    response = get_eval_summary(
        labels=[conference.conference_slug, "Conference"])
    header = ['Class',
              'Teacher(s)',
              'Time',
              '# Interested',
              '# Evaluations']
    for question in response.questions:
        header += [question.question]
    header += ['Actions']

    display_list = []
    summary_view_data = {}
    events = Class.objects.filter(e_conference=conference)
    for occurrence in response.occurrences:
        class_event = events.get(
                eventitem_id=occurrence.eventitem.eventitem_id)
        teachers = []
        interested = []
        for person in occurrence.people:
            if person.role == "Interested":
                interested += [person]
            elif person.role in ("Teacher", "Moderator"):
                teachers += [Performer.objects.get(pk=person.public_id)]

        display_item = {
            'id': occurrence.id,
            'eventitem_id': class_event.eventitem_id,
            'sort_start': occurrence.start_time,
            'start':  occurrence.start_time.strftime(DATETIME_FORMAT),
            'title': class_event.e_title,
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

    display_list.sort(key=lambda k: k['sort_start'])
    user_message = UserMessage.objects.get_or_create(
        view="InterestView",
        code="ABOUT_EVAL_REPORT",
        defaults={
            'summary': "About Evaluation Report",
            'description': eval_report_explain_msg})
    return render(request,
                  'gbe/report/evals.tmpl',
                  {'header': header,
                   'classes': display_list,
                   'questions': response.questions,
                   'summaries': summary_view_data,
                   'conference_slugs': conference_slugs(),
                   'conference': conference,
                   'about': user_message[0].description,
                   'details': details})
