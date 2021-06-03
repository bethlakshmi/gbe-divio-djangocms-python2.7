from eventbrite import Eventbrite


def get_eb_events(ticketing_events=None):
    eventbrite = Eventbrite('AHKQB5Z7XVGWV5WAAM4F')
    organizations = eventbrite.get('/users/me/organizations/')
    events = eventbrite.get('/organizations/547440371489/events/')
    raise Exception(events['events'])
