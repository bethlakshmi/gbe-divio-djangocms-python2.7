from django.shortcuts import render
from gbe_logging import log_func
from gbe.models import (
    Conference,
    UserMessage,
    Vendor,
)
from gbetext import fashion_fair_intro


@log_func
def FashionFaireView(request):
    '''
    The Vintage Fashion Faire.  Glorified vendor list
    '''
    current_conference = Conference.current_conf()
    if request.GET:
        conference = Conference.by_slug(request.GET.get('conference', None))
    else:
        conference = current_conference
    user_message = UserMessage.objects.get_or_create(
        view="FashionFaireView",
        code="INTRODUCTION",
        defaults={
            'summary': "Top of Fashion Fair Page",
            'description': fashion_fair_intro})
    vendors = list(Vendor.objects.filter(
        accepted=3,
        b_conference=conference).exclude(level="Featured").order_by('b_title'))
    featured_vendors = list(Vendor.objects.filter(
        accepted=3,
        b_conference=conference,
        level="Featured").order_by('b_title'))
    template = 'gbe/fashionfair.tmpl'
    context = {'vendors': vendors,
               'featured_vendors': featured_vendors,
               'user_message': user_message[0]}
    return render(request, template, context)
