from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ClassFactory,
    ClassProposalFactory,
    ConferenceVolunteerFactory,
    PersonaFactory,
    ProfileFactory,
    UserFactory,
)
from tests.functions.gbe_functions import login_as
from gbe.models import ClassProposal
from gbetext import conf_volunteer_save_error


class TestConferenceVolunteer(TestCase):
    '''Tests for conference_volunteer view'''
    view_name = 'conference_volunteer'

    def setUp(self):
        self.client = Client()
        self.performer = PersonaFactory()

    def get_class_form(self):
        return {'name': 'someone@host.com',
                'title': 'some class name',
                'proposal': 'some class description',
                'presenter': 1,
                'bid': 1,
                'how_volunteer': 1
                }

    def test_conference_volunteer_no_visible_class_proposals(self):
        ClassProposal.objects.all().delete()
        proposal = ClassProposalFactory(display=False)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_conference_volunteer_no_profile(self):
        ClassProposal.objects.all().delete()
        proposal = ClassProposalFactory(display=False)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(UserFactory(), self)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_conference_volunteer_post_offer_form_invalid(self):
        proposal = ClassProposalFactory(display=True)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(PersonaFactory().performer_profile, self)

        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        response = self.client.post(url,
                                    data=data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, conf_volunteer_save_error)

    def test_conference_volunteer_post_offer_form_valid(self):
        proposal = ClassProposalFactory(display=True)
        url = reverse(self.view_name, urlconf="gbe.urls")
        persona = PersonaFactory()
        login_as(persona.performer_profile, self)
        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        data["%d-bid" % proposal.pk] = proposal.id
        data['%d-how_volunteer' % proposal.pk] = 'Any of the Above'
        data['%d-presenter' % proposal.pk] = persona.pk
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        expected_string = 'Your profile needs an update'
        self.assertContains(response, expected_string)
        self.assertEqual(response.status_code, 200)

    def test_conference_volunteer_post_offer_existing_volunteer(self):
        proposal = ClassProposalFactory(display=True)
        persona = ConferenceVolunteerFactory(
            bid=proposal).presenter
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(persona.performer_profile, self)
        data = self.get_class_form()
        data["%d-volunteering" % proposal.id] = 1
        data["%d-bid" % proposal.pk] = proposal.id
        data['%d-how_volunteer' % proposal.pk] = 'Any of the Above'
        data['%d-presenter' % proposal.pk] = persona.pk
        response = self.client.post(url,
                                    data=data,
                                    follow=True)
        self.assertRedirects(response, reverse("home", urlconf='gbe.urls'))
        expected_string = 'Your profile needs an update'
        self.assertContains(response, expected_string)
        self.assertEqual(response.status_code, 200)

    def test_conference_volunteer_get(self):
        proposal = ClassProposalFactory(display=True)
        ClassProposalFactory(display=True,
                             type="Panel")
        ClassProposalFactory(display=True,
                             type="Shoe")
        persona = ConferenceVolunteerFactory(
            bid=proposal).presenter
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(persona.performer_profile, self)
        response = self.client.get(url)
        expected_text = "Apply to Present"
        self.assertContains(response, expected_text)
        self.assertEqual(response.status_code, 200)

    def test_conference_volunteer_no_persona(self):
        proposal = ClassProposalFactory(display=True)
        url = reverse(self.view_name, urlconf="gbe.urls")
        login_as(ProfileFactory(), self)
        response = self.client.get(url, follow=True)
        self.assertRedirects(
            response,
            reverse("persona_create",
                    urlconf='gbe.urls') + "?next=/conference/volunteer")
        self.assertEqual(response.status_code, 200)
