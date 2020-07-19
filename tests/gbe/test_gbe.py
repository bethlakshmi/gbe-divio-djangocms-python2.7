from django.test import TestCase


class TestGBE(TestCase):

    def assert_hidden_value(self, response, field_id, name, value):
        self.assertContains(
            response,
            '<input type="hidden" name="%s" value="%s" id="%s" />' % (
                name,
                value,
                field_id),
            html=True)

    def assert_radio_state(self,
                           response,
                           name,
                           button_id,
                           value,
                           checked=False):
        checked_state = ""
        if checked:
            checked_state = "checked "
        checked_button = (
            '<input type="radio" name="%s" value="%s" id="%s" %s/>' % (
                        name, value, button_id, checked_state))
        self.assertContains(response, checked_button, html=True)
