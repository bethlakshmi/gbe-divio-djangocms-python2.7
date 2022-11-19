from django.db.models import (
    BooleanField,
    CharField,
    Model,
    SlugField,
)
from gbetext import (
    act_format,
    conference_statuses
)


class Conference(Model):
    conference_name = CharField(max_length=128)
    conference_slug = SlugField()
    status = CharField(choices=conference_statuses,
                       max_length=50,
                       default='upcoming')
    accepting_bids = BooleanField(default=False)
    act_style = CharField(choices=act_format,
                          max_length=50,
                          default='normal')

    def __str__(self):
        return self.conference_name

    @classmethod
    def current_conf(cls):
        return cls.objects.filter(status__in=('upcoming', 'ongoing')).first()

    @classmethod
    def by_slug(cls, slug):
        try:
            return cls.objects.get(conference_slug=slug)
        except cls.DoesNotExist:
            return cls.current_conf()

    @classmethod
    def all_slugs(cls, current=False):
        slug_filter = cls.objects
        if current:
            slug_filter = slug_filter.exclude(status="completed")

        return slug_filter.order_by('-conference_slug').values_list(
            'conference_slug', flat=True)

    class Meta:
        verbose_name = "conference"
        verbose_name_plural = "conferences"
        app_label = "gbe"
