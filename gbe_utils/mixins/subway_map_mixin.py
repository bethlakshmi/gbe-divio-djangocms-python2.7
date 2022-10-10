from django.urls import reverse_lazy


class SubwayMapMixin():

    place_in_list = {
        'PersonaCreate': 1,
        'TroupeCreate': 1,
    }

    def make_map(self, view_name, target_url):
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
