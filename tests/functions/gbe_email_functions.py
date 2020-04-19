

def assert_checkbox(response,
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
        '%sclass="form-check-input" id="id_%s-%s_%s" />%s'
    assert bytes(checkbox % (prefix,
                             field_name,
                             value,
                             checked_string,
                             prefix,
                             field_name,
                             position,
                             label), 'utf-8') in response.content
