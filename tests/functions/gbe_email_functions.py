

def assert_checkbox(response,
                    field_name,
                    position,
                    value,
                    label,
                    checked=True,
                    prefix="email-select"):
    if checked:
        checked_string = 'checked="checked" '
    else:
        checked_string = ''
    checkbox = '<input %sid="id_%s-%s_%s"' + \
        ' name="%s-%s" type="checkbox" value="%s" />%s'
    assert checkbox % (checked_string,
                       prefix,
                       field_name,
                       position,
                       prefix,
                       field_name,
                       value,
                       label) in response.content
