from gbe.views import ReviewProfilesView
from django.urls import reverse
from gbetext import merge_users_msg


class MergeProfileSelect(ReviewProfilesView):
    page_title = 'Merge Users - Pick Second'
    view_title = 'Merge Users - Pick Second'
    intro_text = merge_users_msg
    view_permissions = ('Registrar', )

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.exclude(pk=self.kwargs['pk'])

    def set_actions(self, profile):
        return [{'url': reverse('merge_profiles',
                                urlconf='gbe.urls',
                                args=[self.kwargs['pk'], profile.pk]),
                 'text': "Merge"}]
