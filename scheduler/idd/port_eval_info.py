from scheduler.models import (
    EventEvalBoolean,
    EventEvalComment,
    EventEvalGrade,
)
from scheduler.data_transfer import GeneralResponse


def port_answer(orig_user, new_user, answer_class):
    for answer in answer_class.objects.filter(user=orig_user):
        if not answer_class.objects.filter(user=new_user,
                                           event=answer.event,
                                           question=answer.question).exists():
            answer.user=new_user
            answer.save()

def port_eval_info(orig_user, new_user):
    port_answer(orig_user, new_user, EventEvalBoolean)
    port_answer(orig_user, new_user, EventEvalGrade)
    port_answer(orig_user, new_user, EventEvalComment)
    return GeneralResponse()
