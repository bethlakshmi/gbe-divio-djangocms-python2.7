from django.views.generic.list import ListView
from gbe.models import Conference
from gbe.functions import get_latest_conference


class ConferenceListView(ListView):
    # uses methods in list view, meant as an add on to any list that offers
    # a list filtered by conference, using the conference pickers
    def setup(self, request, *args, **kwargs):
        if request.GET and request.GET.get('conf_slug'):
            self.conference = Conference.by_slug(request.GET['conf_slug'])
        elif request.GET and request.GET.get('conference'):
            self.conference = Conference.by_slug(request.GET['conference'])
        else:
            self.conference = get_latest_conference()
        return super().setup(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO - consolidate picker templates to one format & reduce context
        context = super().get_context_data(**kwargs)
        context['conference'] = self.conference
        context['conference_slugs'] = Conference.all_slugs()
        context['conf_slug'] = self.conference.conference_slug
        return context
