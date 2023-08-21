# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .choices_provider import get_software_suggestions
from .global_state import global_state
from .page import Page
from .util import SummaryEntry
from .widgets import MultiSelectionRow, reset_model, SelectionRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/software.ui')
class SoftwarePage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'system-software-install-symbolic'

    software_list = Gtk.Template.Child()
    software_model = Gio.ListStore()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)
        self.software_list.bind_model(
            self.software_model,
            self._create_row)

    def _create_row(self, pkg):
        if pkg.options:
            return MultiSelectionRow(pkg.name, pkg.description, pkg.icon_path,
                                     'application-x-executable-symbolic', pkg.options)
        else:
            return SelectionRow(pkg.name, pkg.description, pkg.icon_path,
                                'application-x-executable-symbolic', pkg.suggested, pkg.keyword)

    def _setup_software(self):
        suggestions = get_software_suggestions()
        reset_model(self.software_model, suggestions)

    ### callbacks ###

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self)

    @Gtk.Template.Callback('software_row_activated')
    def _software_row_activated(self, list_box, row):
        if type(row) == SelectionRow:
            row.flip_switch()

    ### public methods ###

    def load_once(self):
        self._setup_software()

    def unload(self):
        summary = []
        packages = []
        for row in self.software_list:
            if type(row) == MultiSelectionRow:
                option = row.get_chosen_option()
                packages.append(option.keyword)
                summary.append(SummaryEntry(option.display, row.icon_path))
            elif type(row) == SelectionRow and row.is_activated():
                packages.append(row.info)
                summary.append(SummaryEntry(row.get_title(), row.icon_path))
        packages = ' '.join(packages)
        global_state.set_config('chosen_software_packages', packages)
        global_state.set_config('chosen_software', summary)
