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
                           checked=False,
                           required=False):
        checked_state = ""
        if checked:
            checked_state = "checked "
        required_state = ""
        if required:
            required_state = "required "
        checked_button = (
            '<input type="radio" name="%s" value="%s" %sid="%s" %s/>' % (
                        name, value, required_state, button_id, checked_state))
        self.assertContains(response, checked_button, html=True)
