from django.views.generic.list import ListView
from gbe_utils.mixins import (
    GbeContextMixin,
    RoleRequiredMixin,
)
from django.db.models import Q
from gbe.models import Conference
from scheduler.idd import get_occurrences
from gbe.reporting.views import PerformerSlidesList


class ShowSlidesView(GbeContextMixin, RoleRequiredMixin, ListView):
    model = Conference
    template_name = 'gbe/report/show_slides.tmpl'
    page_title = 'Show Slide Data'
    view_title = 'Show Slide Data'
    intro_text = '''Each link is a CSV with the data we need for the given
    show's slide deck.  The slides should display behind the performer to
    show their info and contact/tipping data'''
    view_permissions = PerformerSlidesList.view_perm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shows'] = get_occurrences(
                event_styles=['Show'],
                label_sets=[Conference.all_slugs(current=True)]).occurrences
        return context
