from django.urls import (
    reverse,
    reverse_lazy,
)
from django.contrib import messages
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from gbe.models import (
    Article,
    UserMessage,
)
from published.utils import queryset_filter
from gbe.forms import ArticleForm
from published.mixins import PublishedListMixin, PublishedDetailMixin
from gbe_utils.mixins import (
    GbeContextMixin,
    GbeFormMixin,
    FormToTableMixin,
    RoleRequiredMixin,
)
from gbetext import (
    create_article_msg,
    update_article_msg,
    manage_articles_msg,
)
from gbe.email.views import (
    MailToBiddersView,
    MailToPersonView,
    MailToRolesView,
)


article_view_permissions = MailToPersonView.email_permissions + (
    MailToRolesView.reviewer_permissions) + (
    MailToBiddersView.reviewer_permissions)


def fetch_article_context(num_articles=4):
    more = False
    news_articles = Article.objects.order_by('-live_as_of', '-updated_at')
    if queryset_filter(news_articles).count() > num_articles:
        more = True
    return {
        'object_list': queryset_filter(news_articles)[:num_articles],
        'more': more}


class ArticleList(PublishedListMixin, ListView):
    model = Article
    template_name = 'gbe/news/view_list.tmpl'
    context_object_name = 'articles'


class ArticleDetail(PublishedDetailMixin, DetailView):
    model = Article
    template_name = 'gbe/news/view_article.tmpl'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'


class ArticleDetailRestricted(RoleRequiredMixin, DetailView):
    model = Article
    template_name = 'gbe/news/view_article.tmpl'
    context_object_name = 'article'
    view_permissions = article_view_permissions


class ArticleCreate(FormToTableMixin, RoleRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'gbe/admin_html_form.tmpl'
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
    page_title = 'Create News Article'
    view_title = 'Create News Article'
    valid_message = create_article_msg
    view_permissions = article_view_permissions

    def form_valid(self, form):
        response = super(ArticleCreate, self).form_valid(form)
        self.object.creator = self.request.user.profile
        self.object.save()
        return response


class ArticleDelete(GbeFormMixin, RoleRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
    template_name = 'gbe/admin_html_form.tmpl'
    view_permissions = article_view_permissions
    valid_message = "Successfully deleted article."


class ArticleUpdate(FormToTableMixin, RoleRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'gbe/admin_html_form.tmpl'
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
    page_title = 'Update News Article'
    view_title = 'Update News Article'
    valid_message = update_article_msg
    view_permissions = article_view_permissions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse("news-delete",
                                        urlconf="gbe.urls",
                                        args=[self.get_object().pk])
        return context


class ArticleManageList(GbeContextMixin, RoleRequiredMixin, ListView):
    model = Article
    template_name = 'gbe/news/edit_list.tmpl'
    context_object_name = 'articles'
    view_permissions = article_view_permissions
    page_title = 'Manage News Articles'
    view_title = 'Manage News Articles'
    intro_text = manage_articles_msg

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = ['Published?',
                              'Publication Date',
                              'Author',
                              'Slug',
                              'Title',
                              'Summary',
                              'Actions']
        if self.request.GET.get('changed_id', None):
            context['changed_id'] = int(
                self.request.GET.get('changed_id', None))
        return context
