from gbe_utils.mixins import GbeFormMixin


class FormToTableMixin(GbeFormMixin):

    def get_success_url(self):
        next_url = self.request.GET.get('next', self.success_url)
        if "?" in next_url:
            next_url = next_url[:next_url.index("?")]
        return "%s?changed_id=%d" % (
            next_url,
            self.object.pk)
