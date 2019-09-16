from django.template import (
    loader,
    RequestContext,
)
from django.http import HttpResponse

from gbe_logging import log_func


@log_func
def DownView(request):
    '''
    Static "Site down" notice. Simply refers user to a static template
    with a message.
    '''
    template = loader.get_template('down.tmpl')
    context = RequestContext(request, {})
    return HttpResponse(template.render(context))
