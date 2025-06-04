# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gio, Gtk, Vte

from .terminal_provider import terminal_provider
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/terminal_dialog.ui')
class TerminalDialog(Adw.Dialog):
    __gtype_name__ = __qualname__

    copy_button_content = Gtk.Template.Child()
    placeholder = Gtk.Template.Child()

    def __init__(self, terminal, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.copy_button_content)

        self._setup_actions()

        self.placeholder.set_child(terminal_provider.steal())

    def _setup_actions(self):
        # add terminal copy shortcuts
        self.action_group = Gio.SimpleActionGroup()
        action_name = 'copy'
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', lambda _, __: self._copy())
        self.action_group.add_action(action)
        self.insert_action_group('terminal', self.action_group)

    def _copy(self):
        terminal = self.placeholder.get_child()
        if terminal.get_has_selection():
            terminal.copy_clipboard()
            terminal.unselect_all()
        else:
            text, _ = terminal.get_text_range_format(
                Vte.Format.TEXT, 0, 0, terminal.get_scrollback_lines(), 0)
            self.get_clipboard().set(text.strip())

    ### callbacks ###

    @Gtk.Template.Callback('closed')
    def _terminal_closed(self, dialog):
        self.placeholder.set_child(None)
        terminal_provider.stash()
