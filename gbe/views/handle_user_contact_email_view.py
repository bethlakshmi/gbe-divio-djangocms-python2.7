from django.http import HttpResponseRedirect
from django.urls import reverse
from gbe.forms import ContactForm
from gbe.email.functions import send_user_contact_email
from gbe_logging import log_func
from django.conf import settings


@log_func
def HandleUserContactEmailView(request):
    return_redirect = HttpResponseRedirect(reverse('home',
                                                   urlconf='gbe.urls',
                                                   args=[]))
    if request.method != 'POST':
        return return_redirect
    form = ContactForm(request.POST)
    if not form.is_valid():
        return return_redirect
    data = form.cleaned_data
    name = data.get('name', 'UNKNOWN USER')
    user_address = data.get('email', 'UNKNOWN ADDRESS')
    user_msg = data.get('message', 'UNKNOWN MESSAGE')
    format_string = "Burlesque Expo user %s (%s) says: \n\n %s"
    message = format_string % (name,
                               user_address,
                               user_msg)

    from_address = settings.DEFAULT_FROM_EMAIL

    send_user_contact_email(name, from_address, message)
    return return_redirect

    # TO DO: error handling
