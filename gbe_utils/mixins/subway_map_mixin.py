from django.urls import reverse_lazy
from gbe_utils.mixins import GbeFormMixin


class SubwayMapMixin(GbeFormMixin):

    place_in_list = {
        'RegisterView': 0,
        'PersonaCreate': 1,
        'MakeActView': 2,
        'MakeClassView': 2,
        'MakeActViewPayment': 3,
    }

    def get_success_url(self):
        return self.request.GET.get('next', self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subway_map'] = self.get_map(self.__class__.__name__,
                                             self.get_success_url())
        return context

    def get_map(self, view_name, target_url):
        step_lists = {
            reverse_lazy('act_create', urlconf='gbe.urls'):  [
                ['Create Account', 'upcoming'],
                ['Create Bio', 'upcoming'],
                ['Apply', 'upcoming'],
                ['Payment', 'upcoming']],
            reverse_lazy('class_create', urlconf='gbe.urls'):  [
                ['Create Account', 'upcoming'],
                ['Create Bio', 'upcoming'],
                ['Apply', 'upcoming']],
        }
        step_list = None
        if target_url in step_lists and view_name in self.place_in_list:
            step_list = step_lists[target_url]
            active_pos = self.place_in_list[view_name]
            for n in range(active_pos):
                step_list[n][1] = "completed"
            step_list[active_pos][1] = "active"
        return step_list
