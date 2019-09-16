from gbe.models import Class
from gbe.forms import (
    ClassBidForm,
    PersonaForm,
)
from gbe.views import ViewBidView
from gbe.views.class_display_functions import get_scheduling_info


class ViewClassView(ViewBidView):
    bid_type = Class
    object_form_type = ClassBidForm
    viewer_permissions = ('Class Reviewers',)
    bid_prefix = 'The Class'
    owner_prefix = 'The Teacher(s)'

    def get_owner_profile(self):
        return self.bid.teacher.contact

    def make_context(self):
        context = {'performer': self.bid.teacher,
                   'class': self.bid,
                   'scheduling_info': get_scheduling_info(self.bid),
                   'display_contact_info': True}
        return context
