# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .global_state import global_state
from .language_provider import language_provider
from .page import Page
from .system_calls import set_system_language
from .widgets import reset_model, ProgressRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/language.ui')
class LanguagePage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'language-symbolic'

    suggested_list = Gtk.Template.Child()
    suggested_model = Gtk.Template.Child()

    other_list = Gtk.Template.Child()
    other_model = Gtk.Template.Child()

    language_chosen = False

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        # models
        self.suggested_list.bind_model(self.suggested_model, lambda o: ProgressRow(o.name, o))
        self.other_list.bind_model(self.other_model, lambda o: ProgressRow(o.name, o))

    ### callbacks ###

    @Gtk.Template.Callback('language_row_activated')
    def _language_row_activated(self, list_box, row):
        if (not self.language_chosen or
                global_state.get_config('language_code') != row.info.language_code):
            self.language_chosen = True
            set_system_language(row.info)
            global_state.retranslate_pages()
        global_state.advance(self)

    ### public methods ###

    def load_once(self):
        suggested_languages = language_provider.get_suggested_languages()
        other_languages = language_provider.get_other_languages()
        if not suggested_languages:
            self.suggested_list.set_visible(False)
        if not other_languages:
            self.other_list.set_visible(False)
        
        reset_model(self.suggested_model, suggested_languages)
        reset_model(self.other_model, other_languages)
