from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from tests.factories.gbe_factories import ClassFactory
from tests.functions.gbe_functions import login_as


class TestViewClass(TestCase):
    '''Tests for view_class view'''
    view_name = 'class_view'

    def setUp(self):
        self.client = Client()
        self.class_string = 'Tell Us About Your Class'

    def test_view_class(self):
        '''view_class view, success
        '''
        klass = ClassFactory()
        url = reverse(self.view_name,
                      args=[klass.pk],
                      urlconf='gbe.urls')

        login_as(klass.teacher.performer_profile, self)
        response = self.client.get(url)
        assert response.status_code == 200
