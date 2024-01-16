# View functions for reporting
from gbe_utils.mixins import (
    ConferenceListView,
    CSVResponseMixin,
    RoleRequiredMixin,
)
from gbe.models import (
    Bio,
    Conference,
)
from scheduler.models import PeopleAllocation
from ticketing.models import Transaction
from gbetext import not_scheduled_roles


class EnvStuffView(CSVResponseMixin, RoleRequiredMixin, ConferenceListView):
    model = PeopleAllocation
    template_name = 'CSV'
    file_name = 'env_stuff'
    view_permissions = ('Registrar',)
    room_set_key = 'events'

    def get_queryset(self):
        return self.model.objects.filter(
            event__eventlabel__text=self.conference.conference_slug).exclude(
            role__in=not_scheduled_roles+["Interested"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['header'] = ['Badge Name',
                             'First',
                             'Last',
                             'Tickets',
                             'Personae',
                             'Staff Lead',
                             'Volunteering',
                             'Presenter',
                             'Show']

        people_rows = {}
        # TODO - right now, there is no great IDD that does people class/id AND
        # events.  If that is ever figured out, fix it here
        for commit in self.get_queryset():
            for user in commit.people.users.filter(is_active=True):
                name = user.profile.get_badge_name().encode('utf-8').strip()
                if name not in people_rows.keys():
                    people_rows[name] = {
                        'first': user.first_name.encode('utf-8').strip(),
                        'last': user.last_name.encode('utf-8').strip(),
                        'ticket_names': "",
                        'staff_lead_list': "",
                        'volunteer_list': "",
                        'class_list': "",
                        'personae_list': "",
                        'show_list': "",
                    }
                if commit.role == "Staff Lead":
                    people_rows[name]['staff_lead_list'] += (
                        str(commit.event)+', ')
                elif commit.role == "Volunteer":
                    people_rows[name]['volunteer_list'] += (
                        str(commit.event)+', ')
                elif commit.role in ["Teacher", "Moderator", "Panelist"]:
                    people_rows[name]['class_list'] += (
                        commit.role + ': ' + str(commit.event) + ', ')
                elif commit.role == "Performer" and (
                        "General" in commit.event.labels):
                    people_rows[name]['show_list'] += str(commit.event)+', '

                if commit.people.class_name == "Bio":
                    bio = Bio.objects.get(pk=commit.people.class_id)
                    if str(bio) not in people_rows[name]['personae_list']:
                        people_rows[name]['personae_list'] += str(bio) + ', '

        for t in Transaction.objects.filter(
                ticket_item__ticketing_event__conference=self.conference,
                purchaser__matched_to_user__is_active=True,
                ticket_item__ticketing_event__act_submission_event=False
                ).exclude(purchaser__matched_to_user__username="limbo"
                ).exclude(status="canceled"):
            print(t.purchaser.matched_to_user)
            name = t.purchaser.matched_to_user.profile.get_badge_name(
                ).encode('utf-8').strip()
            if name not in people_rows.keys():
                people_rows[name] = {
                    'first': t.purchaser.matched_to_user.first_name.encode(
                        'utf-8').strip(),
                    'last': t.purchaser.matched_to_user.last_name.encode(
                        'utf-8').strip(),
                    'ticket_names': "",
                    'staff_lead_list': "",
                    'volunteer_list': "",
                    'class_list': "",
                    'personae_list': "",
                    'show_list': "",
                }
            people_rows[name]['ticket_names'] += t.ticket_item.title + ", "

        context['rows'] = []
        for name, details in people_rows.items():
            context['rows'] += [[
                name,
                details['first'],
                details['last'],
                details['ticket_names'],
                details['personae_list'],
                details['staff_lead_list'],
                details['volunteer_list'],
                details['class_list'],
                details['show_list']], ]

        return context
