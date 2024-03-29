# New Event Creation
from .event_wizard_view import EventWizardView
from .class_wizard_view import ClassWizardView
from .rehearsal_wizard_view import RehearsalWizardView
from .staff_area_wizard_view import StaffAreaWizardView
from .ticketed_event_wizard_view import TicketedEventWizardView
from .volunteer_wizard_view import VolunteerWizardView
from .volunteer_autocomplete import VolunteerAutocomplete

# Brand new edit (will deprecate make_occurrence)
from .manage_vol_wizard_view import ManageVolWizardView
from .manage_worker_view import ManageWorkerView
from .edit_event_view import EditEventView
from .edit_class_view import EditClassView
from .edit_show_view import EditShowView
from .edit_volunteer_view import EditVolunteerView
from .edit_staff_area_view import EditStaffAreaView
from .copy_collections_view import CopyCollectionsView
from .copy_occurrence_view import CopyOccurrenceView
from .copy_staff_area_view import CopyStaffAreaView

# Misc
from .manage_events_view import ManageEventsView
from .delete_event_view import DeleteEventView
from .manage_conference_view import ManageConferenceView
from .show_dashboard import ShowDashboard

# Public features
from .show_calendar_view import ShowCalendarView
from .set_favorite_view import SetFavoriteView
from .set_volunteer_view import SetVolunteerView
from .list_events_view import ListEventsView
from .event_detail_view import EventDetailView
from .eval_event_view import EvalEventView
from .volunteer_signup_view import VolunteerSignupView
from .approve_volunteer_view import ApproveVolunteerView
