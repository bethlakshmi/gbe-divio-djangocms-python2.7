from django.db import models
from gbe.models import (
    AvailableInterest,
    Volunteer
)
from gbe_forms_text import rank_interest_options


class VolunteerInterest(models.Model):
    interest = models.ForeignKey(AvailableInterest, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    rank = models.IntegerField(choices=rank_interest_options,
                               blank=True)

    @property
    def rank_description(self):
        return dict(rank_interest_options).get(self.rank, None)

    class Meta:
        app_label = "gbe"
        unique_together = (('interest', 'volunteer'),)
