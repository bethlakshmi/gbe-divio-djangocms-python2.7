from django.test import TestCase
from django.test import Client
from django.urls import reverse
from tests.factories.gbe_factories import (
    ArticleFactory,
    UserFactory,
    UserMessageFactory,
    PersonaFactory,
    ProfileFactory,
    SocialLinkFactory,
)
from tests.functions.gbe_functions import (
    assert_alert_exists,
    grant_privilege,
    login_as,
    set_image,
)
from gbetext import (
    update_article_msg,
)
from gbe.models import (
    Article,
    UserMessage,
)
from tests.gbe.test_gbe import TestGBE


formset_data = {
    'title': 'Article Title',
    'summary': 'Summarized',
    'content': '<b>bold</b> and other stuff <br><br>more lines!',
    'slug': 'slug-for-article',
    'publish_status': 1,
}


class TestArticleCreate(TestCase):
    '''Tests for index view'''
    view_name = 'news-add'

    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Act Coordinator')
        cls.url = reverse(cls.view_name, urlconf='gbe.urls')

    def test_get(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            '<textarea name="content" cols="40" rows="10" id="admin-tiny-' +
            'mce">\n</textarea>',
            html=True)

    def test_submit(self):
        ''' using an image and making a custom success message
        '''
        msg = UserMessageFactory(
            view='ArticleCreate',
            code='SUCCESS')
        login_as(self.privileged_user, self)
        article_count = Article.objects.all().count()
        response = self.client.post(
            self.url,
            formset_data,
            follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, Article.objects.all().count()-article_count)
        latest = Article.objects.order_by('-created_at').first()
        assert_alert_exists(
            response, 'success', 'Success', msg.description)
        self.assertRedirects(response, "%s?changed_id=%d" %(
            reverse('news_manage', urlconf='gbe.urls'),
            latest.pk))

    def test_submit_invalid(self):
        # no pronoun values supplied in either field
        login_as(self.privileged_user, self)
        article_count = Article.objects.all().count()
        response = self.client.post(self.url, {
            'summary': 'Summarized',
            'content': '<b>bold</b> and other stuff <br><br>more lines!',
            'slug': 'slug-for-article',
            'publish_status': 1,
            })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.", 1)
        self.assertEqual(article_count, Article.objects.all().count())


class TestArticleUpdate(TestGBE):
    view_name = 'news-update'

    '''Tests for edit_persona view'''
    def setUp(self):
        UserMessage.objects.all().delete()
        self.client = Client()

    @classmethod
    def setUpTestData(cls):
        cls.privileged_user = ProfileFactory().user_object
        grant_privilege(cls.privileged_user, 'Act Coordinator')
        cls.article = ArticleFactory()
        cls.url = reverse(cls.view_name,
                          urlconf='gbe.urls',
                          args=[cls.article.pk])

    def test_get(self):
        login_as(self.privileged_user, self)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a href="#" data-toggle="modal" data-target="#DeleteModal" ' +
            'data-backdrop="true" class="btn gbe-btn-secondary">Delete</a>',
            html=True)
        self.assertContains(
            response,
            reverse("news-delete",
                    urlconf="gbe.urls",
                    args=[self.article.pk]))
        self.assertContains(
            response,
            ('<input type="text" name="title" value="%s" maxlength="128" ' +
             'id="id_title">') % self.article.title,
            html=True)

    def test_submit(self):
        login_as(self.privileged_user, self)
        response = self.client.post(
            self.url,
            formset_data,
            follow=True
        )
        article_reloaded = Article.objects.get(pk=self.article.pk)
        self.assertEqual(article_reloaded.title, formset_data['title'])
        self.assertRedirects(response, "%s?changed_id=%d" %(
            reverse('news_manage', urlconf='gbe.urls'),
            article_reloaded.pk))
        assert_alert_exists(
            response, 'success', 'Success', update_article_msg)
