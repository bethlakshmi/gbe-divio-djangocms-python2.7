from django.test import TestCase


class TestFilters(TestCase):
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

        if prefix is not None:
            checkbox = (
                '<input type="checkbox" name="%s-%s" value="%s" ' + \
                'class="form-check-input" id="id_%s-%s_%s" %s/>%s') % (
                prefix,
                field_name,
                value,
                prefix,
                field_name,
                position,
                checked_string,
                label)
        else:
            checkbox = (
                '<input type="checkbox" name="%s" value="%s" ' + \
                'class="form-check-input" id="id_%s_%s" %s/>%s') % (
                field_name,
                value,
                field_name,
                position,
                checked_string,
                label)

        self.assertContains(response, checkbox, html=True)
