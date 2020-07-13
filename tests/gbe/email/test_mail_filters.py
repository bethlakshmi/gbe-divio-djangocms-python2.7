from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import ProfileFactory
from tests.functions.gbe_functions import grant_privilege
from django.contrib.auth.models import User
from gbe.models import Conference


class TestMailFilters(TestCase):
    def assert_checkbox(self,
                        response,
                        field_name,
                        position,
                        value,
                        label,
                        checked=True,
                        prefix="email-select"):
        if checked:
            checked_string = 'checked '
        else:
            checked_string = ''
        checkbox = '<input type="checkbox" name="%s-%s" value="%s" ' + \
            'class="form-check-input" id="id_%s-%s_%s" %s/>%s'
        self.assertContains(response, checkbox % (
            prefix,
            field_name,
            value,
            prefix,
            field_name,
            position,
            checked_string,
            label), html=True)
