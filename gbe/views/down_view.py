from django.shortcuts import render

from gbe_logging import log_func


@log_func
def DownView(request):
    '''
    Static "Site down" notice. Simply refers user to a static template
    with a message.
    '''
    return render(request, 'down.tmpl', {})
