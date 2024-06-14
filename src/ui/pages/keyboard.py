# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .config import config
from .global_state import global_state
from .keyboard_layout_provider import get_default_layout, get_layouts_for
from .language_provider import language_provider
from .page import Page
from .system_calls import set_system_keyboard_layout
from .widgets import reset_model, ProgressRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/keyboard_language.ui')
class KeyboardLanguagePage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'input-keyboard-symbolic'

    list = Gtk.Template.Child()
    model = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.model.splice(0, 0, language_provider.get_all_languages())
        self.list.bind_model(self.model, lambda o: ProgressRow(o.name, o))

    ### callbacks ###

    @Gtk.Template.Callback('language_row_activated')
    def _language_row_activated(self, list_box, row):
        info = row.info
        config.set('keyboard_language', (info.language_code, info.name))
        global_state.advance(self)


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/keyboard_layout.ui')
class KeyboardLayoutPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'input-keyboard-symbolic'

    language_row = Gtk.Template.Child()
    layout_list = Gtk.Template.Child()
    model = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.loaded_language = ''
        self.layout_list.bind_model(
            self.model, lambda o: ProgressRow(o.name, o))

    ### callbacks ###

    @Gtk.Template.Callback('layout_row_activated')
    def _layout_row_activated(self, list_box, row):
        # use selected keyboard layout
        keyboard = row.info
        config.set('keyboard_layout', (keyboard.layout, keyboard.name))
        set_system_keyboard_layout(keyboard.layout)
        global_state.advance(self)

    @Gtk.Template.Callback('show_language_selection')
    def _show_language_selection(self, row):
        global_state.navigate_to_page("keyboard-language")

    ### public methods ###

    def load(self):
        language_code, language_name  = config.get('keyboard_language')

        if self.loaded_language != language_code:
            self.loaded_language = language_code
            print(f'keyboard_language {language_name}')
            self.language_row.set_subtitle(language_name)

            # fill list with all keyboard layouts for language
            layouts = get_layouts_for(language_code, language_name)
            reset_model(self.model, layouts)


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/keyboard_overview.ui')
class KeyboardOverviewPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'input-keyboard-symbolic'

    primary_layout_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        # page gets reconstructed if different app language is chosen
        language_code, language = config.get('language')
        keyboard = get_default_layout(language_code)

        # TODO: do this in separate manager
        config.set('keyboard_language', (language_code, language))
        config.set('keyboard_layout', (keyboard.layout, keyboard.name))
        set_system_keyboard_layout(keyboard.layout)

    ### callbacks ###

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self)

    @Gtk.Template.Callback('show_layout_selection')
    def _show_layout_selection(self, row):
        global_state.navigate_to_page("keyboard-layout")

    ### public methods ###

    def load(self):
        _, layout_name = config.get('keyboard_layout')
        self.primary_layout_row.set_title(layout_name)
