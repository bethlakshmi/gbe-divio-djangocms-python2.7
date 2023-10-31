from dal import autocomplete
from django.db.models import Q
from gbe.models import ClassLabel
from gbe.functions import validate_perms


class ClassLabelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not validate_perms(self.request, ['Class Coordinator']):
            return ClassLabel.objects.none()

        qs = ClassLabel.objects.all()

        if self.q:
            qs = ClassLabel.objects.filter(
                Q(text__icontains=self.q))

        return qs
