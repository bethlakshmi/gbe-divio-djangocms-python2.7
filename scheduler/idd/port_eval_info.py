from scheduler.models import (
    EventEvalGrade,
    EventEvalBoolean,
    EventEvalQuestion,
)
from scheduler.data_transfer import GeneralResponse


def port_eval_info(orig_user, new_user):
    EventEvalBoolean.objects.filter(user=orig_user).update(new_user)
    EventEvalGrade.objects.filter(user=orig_user).update(new_user)
    EventEvalComment.objects.filter(user=orig_user).update(new_user)
    return GeneralResponse()
