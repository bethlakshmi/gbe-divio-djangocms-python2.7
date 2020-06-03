from django.apps import AppConfig


class TicketingConfig(AppConfig):
    name = 'ticketing'
    verbose_name = "Ticketing"

    def ready(self):
        import ticketing.signals
