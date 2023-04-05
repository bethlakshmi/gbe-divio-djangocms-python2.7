from django.views.generic import DetailView, ListView
from gbe.models import Article
from published.mixins import PublishedListMixin, PublishedDetailMixin

class ArticleListView(PublishedListMixin, ListView):
    model = Article
    template_name = 'gbe/news/view_list.tmpl'
    context_object_name = 'articles'

class ArticleDetailView(PublishedDetailMixin, DetailView):
    model = Article
    template_name = 'gbe/news/view_detail.tmpl'
    context_object_name = 'article'
