from gbe.forms import (
    PersonaForm,
    ClassBidForm,
)
from gbe.models import Class
from gbe.views import ReviewBidView
from gbe.views.class_display_functions import get_scheduling_info


class ReviewClassView(ReviewBidView):
    reviewer_permissions = ('Class Reviewers',)
    coordinator_permissions = ('Class Coordinator',)
    bid_prefix = "The Class"
    bidder_prefix = "The Teacher(s)"
    bidder_form_type = PersonaForm
    bid_form_type = ClassBidForm
    object_type = Class
    bid_view_name = 'class_view'
    review_list_view_name = 'class_review_list'
    changestate_view_name = 'class_changestate'

    def groundwork(self, request, args, kwargs):
        super(ReviewClassView, self).groundwork(request, args, kwargs)
        self.readonlyform_pieces = None
        self.performer = self.object.teacher

    def make_context(self):
        context = super(ReviewClassView, self).make_context()
        context['class'] = self.object
        context['scheduling_info'] = get_scheduling_info(self.object)
        context['performer'] = self.performer
        context['display_contact_info'] = True
        return context
