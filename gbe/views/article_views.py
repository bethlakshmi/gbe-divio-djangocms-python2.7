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
from gbe.forms import ArticleForm
from published.mixins import PublishedListMixin, PublishedDetailMixin
from gbe_utils.mixins import (
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


class ArticleList(PublishedListMixin, ListView):
    model = Article
    template_name = 'gbe/news/view_list.tmpl'
    context_object_name = 'articles'


class ArticleDetail(PublishedDetailMixin, DetailView):
    model = Article
    template_name = 'gbe/news/view_article.tmpl'
    context_object_name = 'article'
    slug_url_kwarg = 'slug'


class ArticleCreate(FormToTableMixin, RoleRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'gbe/modal_performer_form.tmpl'
    no_tabs = True
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
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


class ArticleDelete(RoleRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
    template_name = 'gbe/modal_performer_form.tmpl'
    view_permissions = MailToPersonView.email_permissions + (
        MailToRolesView.reviewer_permissions) + (
        MailToBiddersView.reviewer_permissions)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_tabs'] = True
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        msg = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="SUCCESS",
            defaults={'summary': "Successful Delete",
                      'description': "Successfully deleted article '%s'"})
        messages.success(self.request, msg[0].description % str(obj))
        return super(ArticleDelete, self).delete(request, *args, **kwargs)


class ArticleUpdate(FormToTableMixin, RoleRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    no_tabs = True
    template_name = 'gbe/modal_performer_form.tmpl'
    success_url = reverse_lazy('news_manage', urlconf="gbe.urls")
    page_title = 'Update News Article'
    view_title = 'Update News Article'
    mode = "update"
    valid_message = update_article_msg
    view_permissions = MailToPersonView.email_permissions + (
        MailToRolesView.reviewer_permissions) + (
        MailToBiddersView.reviewer_permissions)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_url'] = reverse("news-delete",
                                        urlconf="gbe.urls",
                                        args=[self.get_object().pk])
        return context


class ArticleManageList(RoleRequiredMixin, ListView):  
    model = Article
    template_name = 'gbe/news/edit_list.tmpl'
    context_object_name = 'articles'
    view_permissions = MailToPersonView.email_permissions + (
        MailToRolesView.reviewer_permissions) + (
        MailToBiddersView.reviewer_permissions)
    page_title = 'Manage News Articles'
    view_title = 'Manage News Articles'
    intro_text = manage_articles_msg

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="PAGE_TITLE",
            defaults={
                'summary': "%s Page Title" % self.__class__.__name__,
                'description': self.page_title})[0].description
        context['view_title'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="VIEW_TITLE",
            defaults={
                'summary': "%s First Header" % self.__class__.__name__,
                'description': self.view_title})[0].description
        if not hasattr(self, 'intro_text'):
            self.intro_text = ""
        context['intro_text'] = UserMessage.objects.get_or_create(
            view=self.__class__.__name__,
            code="INSTRUCTIONS",
            defaults={
                'summary': "%s Instructions" % self.__class__.__name__,
                'description': self.intro_text})[0].description
        context['columns'] = ['Published?',
                              'Publication Date',
                              'Author',
                              'Title',
                              'Summary',
                              'Actions']
        if self.request.GET.get('changed_id', None):
            context['changed_id'] = int(
                self.request.GET.get('changed_id', None))
        return context
