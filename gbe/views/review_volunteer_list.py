from django.views.generic import ListView
from gbe_utils.mixins import (
    ConferenceListView,
    GbeContextMixin,
    RoleRequiredMixin,
)
from gbetext import review_vol_msg
from scheduler.idd import get_people
from gbe.scheduling.views.functions import show_general_status
from gbe.models import VolunteerEvaluation


class ReviewVolunteerList(RoleRequiredMixin, ConferenceListView):
    model = VolunteerEvaluation
    template_name = 'gbe/volunteer_review_list.tmpl'
    context_object_name = 'reviews'
    page_title = 'Review Volunteers'
    view_title = 'Review Volunteers'
    intro_text = review_vol_msg
    view_permissions = 'any'
    
    def get_queryset(self):
        return self.model.objects.filter(
            conference=self.conference).select_related('evaluator')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_id = -1
        if self.request.GET.get('changed_id', None):
            profile_id = int(self.request.GET.get('changed_id', None))
        response = get_people(
            labels=[self.conference.conference_slug],
            roles=["Volunteer"])
        show_general_status(self.request, response, self.__class__.__name__)
        rows = {}
        response.people.sort(key=lambda x: x.occurrence.start_time)
        for people in response.people:
            for user in people.users:
                if user.profile not in rows.keys():
                    review_query = context['reviews'].filter(
                            volunteer=user.profile)
                    rows[user.profile] = {
                        'schedule': [people.occurrence],
                        'reviews': review_query,
                        'status': "",
                        'review_url': "here",
                    }
                    if not user.profile.is_active:
                        row['status'] = "gbe-table-danger"
                    elif user.profile.pk == profile_id:
                        row['status'] = 'gbe-table-success'
                    # elif not review_query.filter(
                    #    evaluator=self.reviewer).exists():
                    #    bid_row['status'] = "gbe-table-info"
                else:
                    rows[user.profile]['schedule'] += [people.occurrence]
        context['rows'] = rows
        context['columns'] = ["Volunteer", "Schedule", "Reviews", "Actions"]
        return context
