# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .config import config
from .global_state import global_state
from .installation_scripting import installation_scripting
from .page import Page
from .widgets import reset_model, SummaryRow

def _filter_chosen_choices(choices):
    return [choice for choice in choices if choice.options or choice.state]

@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/summary.ui')
class SummaryPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__

    # rows
    language_row = Gtk.Template.Child()
    keyboard_row = Gtk.Template.Child()
    user_row = Gtk.Template.Child()
    format_row = Gtk.Template.Child()
    timezone_row = Gtk.Template.Child()
    software_row = Gtk.Template.Child()
    feature_row = Gtk.Template.Child()

    # user row specific
    user_autologin = Gtk.Template.Child()

    # software list
    software_stack = Gtk.Template.Child()
    software_list = Gtk.Template.Child()
    software_model = Gio.ListStore()

    # feature list
    feature_stack = Gtk.Template.Child()
    feature_list = Gtk.Template.Child()
    feature_model = Gio.ListStore()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)
        self.software_list.bind_model(self.software_model, SummaryRow)
        self.feature_list.bind_model(self.feature_model, SummaryRow)
        self.language_row.set_visible(config.get('fixed_language'))
        self.software_row.set_visible(config.get('additional_software'))
        self.feature_row.set_visible(config.get('additional_features'))
        self.user_row.set_visible(not config.get('skip_user'))
        self.format_row.set_visible(not config.get('skip_locale'))
        self.timezone_row.set_visible(not config.get('skip_locale'))

    ### callbacks ###

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self, allow_return=False)
        installation_scripting.can_run_configure()

    @Gtk.Template.Callback('summary_row_activated')
    def _summary_row_activated(self, list_box, row):
        global_state.navigate_to_page(row.get_name())

    ### public methods ###

    def load(self):
        self.language_row.set_subtitle(config.get('language')[1])
        self.keyboard_row.set_subtitle(config.get('keyboard_layout')[1])
        self.user_row.set_subtitle(config.get('user_name'))
        self.user_autologin.set_visible(config.get('user_autologin'))
        self.format_row.set_subtitle(config.get('formats_ui'))
        self.timezone_row.set_subtitle(config.get('timezone'))

        if software := config.get('software_choices'):
            self.software_stack.set_visible_child_name('used')
            reset_model(self.software_model, _filter_chosen_choices(software))
        else:
            self.software_stack.set_visible_child_name('none')

        if features := config.get('feature_choices'):
            self.feature_stack.set_visible_child_name('used')
            reset_model(self.feature_model, _filter_chosen_choices(features))
        else:
            self.feature_stack.set_visible_child_name('none')
