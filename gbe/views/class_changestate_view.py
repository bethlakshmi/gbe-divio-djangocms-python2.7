from django.urls import reverse
from gbe_logging import log_func
from gbe.views import BidChangeStateView
from gbe.models import (
    Class,
    UserMessage,
)
from scheduler.idd import delete_occurrences
from gbe.scheduling.views.functions import show_general_status
from gbe.forms import ClassStateChangeForm
from gbetext import (
    acceptance_states,
    class_status_change_msg,
)
from django.contrib import messages


class ClassChangeStateView(BidChangeStateView):
    object_type = Class
    coordinator_permissions = ('Class Coordinator', )
    redirectURL = 'class_review_list'
    bid_state_change_form = ClassStateChangeForm

    @log_func
    def bid_state_change(self, request):
        # if the class has been rejected/no decision, clear any schedule items.
        user_message = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="CLASS_NOT_ACCEPTED",
            defaults={
                'summary': "Class State Changed (Not Accepted)",
                'description': class_status_change_msg})

        if request.POST['accepted'] not in ('2', '3'):
            response = delete_occurrences(self.object_type.__name__,
                                          self.object.pk)
            show_general_status(
                request,
                response,
                self.__class__.__name__,
                mask_code="OCCURRENCE_NOT_FOUND")
        else:
            if int(request.POST['accepted']) == 3 and (
                    'extra_button' in request.POST.keys()):
                self.next_page = "%s?accepted_class=%d" % (
                    reverse("create_class_wizard",
                            urlconf='gbe.scheduling.urls',
                            args=[self.object.b_conference.conference_slug]),
                    self.object.pk)
            if int(request.POST['accepted']) == 3:
                user_message = UserMessage.objects.get_or_create(
                    view=self.__class__.__name__,
                    code="CLASS_ACCEPTED",
                    defaults={
                        'summary': "Class State Changed (Accepted)",
                        'description': class_status_change_msg})

        messages.success(
            request,
            "%s<br>Teacher/Class: %s - %s<br>State: %s" % (
                user_message[0].description,
                self.object.teacher_bio.name,
                self.object.b_title,
                acceptance_states[int(request.POST['accepted'])][1]))
        return super(ClassChangeStateView, self).bid_state_change(request)
