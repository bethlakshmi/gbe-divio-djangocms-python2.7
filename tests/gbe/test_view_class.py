from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.contexts import ClassContext
from tests.functions.gbe_functions import (
    login_as,
    setup_social_media
)


class TestViewClass(TestCase):
    '''Tests for view_class view'''
    view_name = 'class_view'

    def setUp(self):
        self.client = Client()
        self.class_string = 'Tell Us About Your Class'

    def test_view_class(self):
        '''view_class view, success
        '''
        context = ClassContext()
        link = context.set_social_media("Instagram")
        url = reverse(self.view_name,
                      args=[context.bid.pk],
                      urlconf='gbe.urls')

        login_as(context.teacher.performer_profile, self)
        response = self.client.get(url)
        assert response.status_code == 200
        self.assertContains(response, setup_social_media(link))
