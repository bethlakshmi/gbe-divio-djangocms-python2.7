from gbe_logging import log_func
from gbe.views import BidChangeStateView
from gbe.models import Class


class ClassChangeStateView(BidChangeStateView):
    object_type = Class
    coordinator_permissions = ('Class Coordinator', )
    redirectURL = 'class_review_list'

    @log_func
    def bid_state_change(self, request):
        # if the class has been rejected/no decision, clear any schedule items.
        if request.POST['accepted'] not in ('2', '3'):
            self.object.scheduler_events.all().delete()
        else:
            # We have to keep b_ and e_ data consistent somehow
            # this seems like a good point, as bid editing and event
            # editing are quite different
            self.object.e_title = self.object.b_title
            self.object.e_description = self.object.b_description
        return super(ClassChangeStateView, self).bid_state_change(
            request)
