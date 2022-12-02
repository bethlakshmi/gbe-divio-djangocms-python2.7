from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from gbe_logging import log_func


@log_func
def LogoutView(request):
    '''
    End the current user's session.
    '''
    # if there's any cleanup to do, do it here.
    logout(request)
    return HttpResponseRedirect(reverse('home', urlconf='gbe.urls'))
