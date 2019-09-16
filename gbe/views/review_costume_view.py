from gbe.forms import (
    CostumeBidSubmitForm,
    CostumeDetailsSubmitForm,
    PersonaForm,
)
from gbe.models import (
    Costume,
    Performer,
)
from gbe.views import ReviewBidView
from gbe.views.functions import get_participant_form


class ReviewCostumeView(ReviewBidView):
    reviewer_permissions = ('Costume Reviewers',)
    coordinator_permissions = ('Costume Coordinator',)
    performer_prefix = "The Performer"
    bidder_prefix = "The Owner"
    bid_prefix = "The Costume"
    bidder_form_type = PersonaForm
    object_type = Costume
    bid_form_type = CostumeBidSubmitForm
    bid_view_name = "costume_view"
    review_list_view_name = 'costume_review_list'
    changestate_view_name = 'costume_changestate'

    def groundwork(self, request, args, kwargs):
        super(ReviewCostumeView, self).groundwork(request, args, kwargs)
        self.details = CostumeDetailsSubmitForm(instance=self.object)
        if self.object.performer:
            self.performer = self.bidder_form_type(
                instance=self.object.performer,
                prefix=self.performer_prefix)
        else:
            self.performer = ""
        self.create_object_form()
        if self.object.performer:
            self.object_form['performer'].queryset = Performer.objects.filter(
                pk=self.object.performer.pk)

        self.profile = get_participant_form(
            self.object.profile,
            prefix=self.bidder_prefix)

        self.readonlyform_pieces = [
            self.object_form,
            self.details,
            self.performer,
            self.profile]
