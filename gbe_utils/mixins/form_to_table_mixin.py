from gbe_utils.mixins import GbeFormMixin


class FormToTableMixin(GbeFormMixin):

    def get_success_url(self):
        return "%s?changed_id=%d" % (
            self.request.GET.get('next', self.success_url),
            self.object.pk)
