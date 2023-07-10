import csv
from django.http import HttpResponse
from django.views.generic import TemplateView


class CSVResponseMixin(object):
    """
    A generic mixin that constructs a CSV response.  Requires file_name,
    and for the context to include 'header' and 'rows' - anything else
    will be omitted/ignored
    """
    def render_to_response(self, context, **response_kwargs):
        """
        Creates a CSV response if requested, otherwise returns the default
        template response.
        """
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % (
            self.file_name)

        writer = csv.writer(response)
        writer.writerow(context['header'])

        # Write the data from the context somehow
        for item in context['rows']:
            print(item)
            writer.writerow(item)

        return response
