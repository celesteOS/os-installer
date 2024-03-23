# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum
from gi.repository import Gio, Gtk

from .choices_provider import choices_provider
from .global_state import global_state
from .page import Page
from .util import SummaryEntry
from .widgets import MultiSelectionRow, reset_model, SelectionRow


class ChoiceType(Enum):
    feature = 0
    software = 1


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/choices.ui')
class ChoicesPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__

    list = Gtk.Template.Child()
    software_header = Gtk.Template.Child()
    feature_header = Gtk.Template.Child()
    model = Gtk.Template.Child()

    def __init__(self, choice_type, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.type = choice_type
        match self.type:
            case ChoiceType.feature:
                self.image = 'puzzle-piece-symbolic'
                self.feature_header.set_visible(True)
                self.list_provider = choices_provider.get_feature_suggestions
            case ChoiceType.software:
                self.image = 'system-software-install-symbolic'
                self.software_header.set_visible(True)
                self.list_provider = choices_provider.get_software_suggestions
            case _:
                print("Unknown choice type!")
                exit(0)

        self.list.bind_model(self.model, self._create_row)

    def _create_row(self, choice):
        if choice.options:
            return MultiSelectionRow(choice.name, choice.description, choice.icon_path,
                                     'application-x-executable-symbolic',
                                     choice.options)
        else:
            return SelectionRow(choice.name, choice.description, choice.icon_path,
                                'application-x-executable-symbolic',
                                choice.suggested, choice.keyword)

    ### callbacks ###

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self)

    @Gtk.Template.Callback('row_activated')
    def _row_activated(self, list_box, row):
        if type(row) == SelectionRow:
            row.flip_switch()

    ### public methods ###

    def load_once(self):
        reset_model(self.model, self.list_provider())

    def unload(self):
        summary = []
        keywords = []
        for row in self.list:
            if type(row) == MultiSelectionRow:
                option = row.get_chosen_option()
                keywords.append(option.keyword)
                summary.append(SummaryEntry(option.display, row.icon_path))
            elif type(row) == SelectionRow and row.is_activated():
                keywords.append(row.info)
                summary.append(SummaryEntry(row.get_title(), row.icon_path))
        keywords = ' '.join(keywords)
        match self.type:
            case ChoiceType.feature:
                global_state.set_config('chosen_feature_names', keywords)
                global_state.set_config('chosen_features', summary)
            case ChoiceType.software:
                global_state.set_config('chosen_software_packages', keywords)
                global_state.set_config('chosen_software', summary)


FeaturePage = lambda **args: ChoicesPage(ChoiceType.feature, **args)
SoftwarePage = lambda **args: ChoicesPage(ChoiceType.software, **args)
