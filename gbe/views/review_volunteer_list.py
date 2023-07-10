from django.views.generic import ListView
from gbe_utils.mixins import RoleRequiredMixin


class VolunteerReviewList(RoleRequiredMixin, ListView):
