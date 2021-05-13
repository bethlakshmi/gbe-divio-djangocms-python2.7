from gbe.views import BidChangeStateView
from gbe.models import Costume


class CostumeChangeStateView(BidChangeStateView):
    object_type = Costume
    coordinator_permissions = ('Costume Coordinator', )
    redirectURL = 'costume_review_list'
