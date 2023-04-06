from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
)
from gbe.models import Article
from gbe.forms import ArticleForm
from published.mixins import PublishedListMixin, PublishedDetailMixin
from gbe_utils.mixins import (
    GbeFormMixin,
    RoleRequiredMixin,
)
from gbetext import (
    create_article_msg,
    update_article_msg,
)
from gbe.email.views import (
    MailToBiddersView,
    MailToPersonView,
    MailToRolesView,
)


class ArticleList(PublishedListMixin, ListView):
    model = Article
    template_name = 'gbe/news/view_list.tmpl'
    context_object_name = 'articles'


class ArticleDetail(PublishedDetailMixin, DetailView):
    model = Article
    template_name = 'gbe/news/view_article.tmpl'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'


class ArticleCreate(GbeFormMixin, RoleRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('news_list', urlconf="gbe.urls")
    page_title = 'Create News Article'
    view_title = 'Create News Article'
    mode = "performer"
    valid_message = create_article_msg
    view_permissions = MailToPersonView.email_permissions + (
        MailToRolesView.reviewer_permissions) + (
        MailToBiddersView.reviewer_permissions)

    def form_valid(self, form):
        response = super(ArticleCreate, self).form_valid(form)
        self.object.creator = self.request.user.profile
        self.object.save()
        return response

class ArticleUpdate(GbeFormMixin, RoleRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('news_list', urlconf="gbe.urls")
    page_title = 'Update News Article'
    view_title = 'Update News Article'
    mode = "update"
    valid_message = update_article_msg
    view_permissions = MailToPersonView.email_permissions + (
        MailToRolesView.reviewer_permissions) + (
        MailToBiddersView.reviewer_permissions)
