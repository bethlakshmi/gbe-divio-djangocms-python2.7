from dal import autocomplete
from django.db.models import Q
from gbe.models import Profile
from gbe.functions import validate_perms


class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        validate_perms(self.request, 'any', require=True)

        qs = Profile.objects.filter(user_object__is_active=True).exclude(
            display_name='')

        if self.q:
            qs = qs.filter(
                Q(display_name__icontains=self.q) |
                Q(user_object__username__icontains=self.q) |
                Q(user_object__first_name__icontains=self.q) |
                Q(user_object__last_name__icontains=self.q))
        return qs
