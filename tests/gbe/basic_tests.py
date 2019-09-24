import gbe.models as conf
import nose.tools as nt
from django.test import TestCase


class BasicTest(TestCase):
    def passing_test(self):
        assert True
