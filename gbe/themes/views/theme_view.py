from django.views.generic import View
from django.http import (
    HttpResponse
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from gbe.models import (
    StyleValue,
    StyleVersion,
)
from django.template import (
    Context,
    loader,
)
from django.conf import settings


class ThemeView(View):
    template = 'gbe/themes/style.css'

    def dispatch(self, *args, **kwargs):
        return super(ThemeView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/css')
        context = {'selectors': {}}
        if request.user.is_authenticated and hasattr(request.user,
                                                     'userstylepreview'):
            version = request.user.userstylepreview.version
        elif "version_id" in kwargs:
            version_id = kwargs.get("version_id")
            version = get_object_or_404(StyleVersion, id=version_id)
        elif settings.DEBUG:
            version = get_object_or_404(StyleVersion, currently_test=True)
        else:
            version = get_object_or_404(StyleVersion, currently_live=True)
        current_values = StyleValue.objects.filter(style_version=version)

        for value in current_values:
            selector = value.style_property.selector.__str__()
            if len(value.value) > 0:
                if selector not in context['selectors'].keys():
                    context['selectors'][selector] = {}
                context['selectors'][selector][
                    value.style_property.style_property] = value.value
            elif value.style_property.value_type == "image" and value.image:
                if selector not in context['selectors'].keys():
                    context['selectors'][selector] = {}
                context['selectors'][selector][
                    value.style_property.style_property] = "url(%s)" % (
                        value.image.url)
        t = loader.get_template(self.template)
        response.write(t.render(context))
        return response
