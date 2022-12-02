from django.urls import reverse
from django.test import TestCase
from django.test import Client
from tests.factories.gbe_factories import (
    EmailTemplateFactory,
    EmailTemplateSenderFactory,
    ProfileFactory,
)
from tests.functions.gbe_functions import (
    grant_privilege,
    is_login_page,
    login_as,
)
from tests.contexts.show_context import ShowContext
from django.conf import settings
from post_office.models import EmailTemplate
from gbetext import (
    save_email_template_success_msg,
    unsub_footer_include,
    unsub_footer_plain_include,
)


class TestEditEmailTemplate(TestCase):
    view_name = 'edit_template'

    def setUp(self):
        self.client = Client()
        self.privileged_profile = ProfileFactory()
        self.sender = EmailTemplateSenderFactory(
            from_email="volunteeremail@notify.com",
            template__name='volunteer schedule update',
            template__subject="test template"
        )
        self.url = reverse(self.view_name,
                           args=[self.sender.template.name],
                           urlconf="gbe.email.urls")

    def get_template_post(self):
        data = {"sender": "new@sender.com",
                "subject": 'New Subject',
                "html_content": '<p><b>New</b> Content</p>',
                "name": self.sender.template.name,
                'submit': "Save Template",
                }

        return data

    def test_no_login_gives_error(self):
        response = self.client.get(self.url, follow=True)
        redirect_url = "%s?next=/email/edit_template/%s" % (
            reverse('login'),
            "volunteer%2520schedule%2520update")
        self.assertRedirects(response, redirect_url)
        self.assertTrue(is_login_page(response))

    def test_no_priv(self):
        login_as(ProfileFactory(), self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_bad_template_w_get(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        url = reverse(self.view_name,
                      urlconf="gbe.email.urls",
                      args=["not a real template"])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_volunteer_schedule_update_exists_w_get(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(self.url)

        self.assertContains(response, self.sender.from_email)
        self.assertContains(response, self.sender.template.subject)
        self.assertContains(response, self.sender.template.html_content)

    def test_act_accept_not_exists_w_get(self):
        context = ShowContext()
        grant_privilege(self.privileged_profile.user_object,
                        'Act Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf="gbe.email.urls",
                    args=["act accepted - %s" % context.show.e_title.lower()]))

        self.assertContains(response, settings.DEFAULT_FROM_EMAIL)
        self.assertContains(response, 'Your act has been cast in %s' % (
            context.show.e_title))
        self.assertContains(
            response,
            'Be sure to fill out your Act Tech Info Page ASAP')

    def test_volunteer_update_notification_not_exists_w_get(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        response = self.client.get(
            reverse(self.view_name,
                    urlconf="gbe.email.urls",
                    args=["volunteer update notification"]))

        self.assertContains(response, settings.DEFAULT_FROM_EMAIL)
        self.assertContains(response, 'Volunteer Update Occurred')
        self.assertContains(
            response,
            '{{bidder}} has made a(n) {{bid_type}} {{action}} for ' +
            '{{conference}}!')

    def test_template_exists_w_post(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        response = self.client.post(self.url, data=data, follow=True)
        updated = EmailTemplate.objects.get(name=self.sender.template.name)
        self.assertRedirects(
            response,
            reverse('list_template', urlconf='gbe.email.urls'))
        self.assertContains(response, save_email_template_success_msg)
        self.assertEqual(updated.sender.from_email, data['sender'])
        self.assertEqual(updated.sender.template.subject, data['subject'])
        self.assertEqual(
            updated.sender.template.content,
            "New Content" + unsub_footer_plain_include)
        self.assertEqual(
            updated.sender.template.html_content,
            data['html_content'] + unsub_footer_include)

    def test_template_not_exists_w_post(self):
        # This is both a test of what happens when a new tempate is posted
        #  AND the case when the template doesn't need a footer.
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        data['name'] = "volunteer update notification"
        response = self.client.post(
            reverse(self.view_name,
                    urlconf="gbe.email.urls",
                    args=["volunteer update notification"]),
            data=data,
            follow=True)
        updated = EmailTemplate.objects.get(name=data['name'])
        self.assertRedirects(
            response,
            reverse('list_template', urlconf='gbe.email.urls'))
        self.assertContains(response, save_email_template_success_msg)
        self.assertEqual(updated.sender.from_email, data['sender'])
        self.assertEqual(updated.sender.template.subject, data['subject'])
        self.assertEqual(updated.sender.template.content, "New Content")
        self.assertEqual(
            updated.sender.template.html_content,
            data['html_content'])

    def test_post_includes_footer(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        data['html_content'] = "keep the footer" + unsub_footer_include
        response = self.client.post(self.url, data=data, follow=True)
        updated = EmailTemplate.objects.get(name=self.sender.template.name)
        self.assertRedirects(
            response,
            reverse('list_template', urlconf='gbe.email.urls'))
        self.assertContains(response, save_email_template_success_msg)
        self.assertEqual(updated.sender.from_email, data['sender'])
        self.assertEqual(updated.sender.template.subject, data['subject'])
        self.assertEqual(
            updated.sender.template.content,
            "keep the footer" + unsub_footer_plain_include)
        self.assertEqual(
            updated.sender.template.html_content,
            data['html_content'])

    def test_daily_schedule_keeps_footer(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        data['name'] = "daily schedule"
        response = self.client.post(self.url, data=data, follow=True)
        updated = EmailTemplate.objects.get(name=data['name'])
        self.assertRedirects(
            response,
            reverse('list_template', urlconf='gbe.email.urls'))
        self.assertContains(response, save_email_template_success_msg)
        self.assertEqual(updated.sender.from_email, data['sender'])
        self.assertEqual(updated.sender.template.subject, data['subject'])
        self.assertEqual(
            updated.sender.template.content,
            "New Content" + unsub_footer_plain_include)
        self.assertEqual(
            updated.sender.template.html_content,
            data['html_content'] + unsub_footer_include)

    def test_template_update_includes_footer(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        data['html_content'] = "New Content" + unsub_footer_include
        response = self.client.post(self.url, data=data, follow=True)
        updated = EmailTemplate.objects.get(name=self.sender.template.name)
        self.assertRedirects(
            response,
            reverse('list_template', urlconf='gbe.email.urls'))
        self.assertContains(response, save_email_template_success_msg)
        self.assertEqual(updated.sender.from_email, data['sender'])
        self.assertEqual(updated.sender.template.subject, data['subject'])
        self.assertEqual(
            updated.sender.template.content,
            "New Content" + unsub_footer_plain_include)
        self.assertEqual(
            updated.sender.template.html_content,
            data['html_content'])

    def test_post_bad_data(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Volunteer Coordinator')
        login_as(self.privileged_profile, self)
        data = self.get_template_post()
        del data['sender']
        response = self.client.post(self.url, data=data, follow=True)
        updated = EmailTemplate.objects.get(name=self.sender.template.name)
        self.assertContains(response, "This field is required")

    def test_costume_duplicate_w_get_no_sender(self):
        grant_privilege(self.privileged_profile.user_object,
                        'Costume Coordinator')
        login_as(self.privileged_profile, self)
        template = EmailTemplateFactory(name='costume duplicate')
        url = reverse(self.view_name,
                      urlconf="gbe.email.urls",
                      args=["costume duplicate"])
        response = self.client.get(url)

        self.assertContains(response, settings.DEFAULT_FROM_EMAIL)
        self.assertContains(response, template.subject)
        self.assertContains(response, template.html_content)
