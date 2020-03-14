from django.forms.widgets import URLInput


class FriendlyURLInput(URLInput):
    input_type = 'text'
    pattern = "(https?://)?\w(\.\w+?)+(/~?\w+)?"
