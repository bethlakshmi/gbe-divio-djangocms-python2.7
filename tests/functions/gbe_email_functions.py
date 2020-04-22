

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
        'class="form-check-input" id="id_%s-%s_%s" %s/>%s'
    assert bytes(checkbox % (prefix,
                             field_name,
                             value,
                             prefix,
                             field_name,
                             position,
                             checked_string,
                             label), 'utf-8') in response.content
