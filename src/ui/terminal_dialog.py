# SPDX-License-Identifier: GPL-3.0-or-later

import ctypes

from gi.repository import Adw, Gio, Gtk, Vte

from .config import config
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/terminal_dialog.ui')
class TerminalDialog(Adw.Dialog):
    __gtype_name__ = __qualname__

    copy_button_content = Gtk.Template.Child()
    placeholder = Gtk.Template.Child()

    def __init__(self, terminal, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.copy_button_content)

        self.scrollback_lines = 10000
        self._setup_actions()

        if not terminal:
            # create a new terminal and use existing PTY for it
            terminal = Vte.Terminal()
            terminal.set_allow_hyperlink(True)
            terminal.set_input_enabled(False)
            terminal.set_scroll_on_output(True)
            terminal.set_scrollback_lines(self.scrollback_lines)

            # add empty line on top for margin
            new_line = (ctypes.c_char * 1).from_buffer_copy(b'\n')
            terminal.feed(new_line)

            pty = config.steal('script_pty')
            terminal.set_pty(pty)
        self.placeholder.set_child(terminal)

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
                Vte.Format.TEXT, 0, 0, self.scrollback_lines, 0)
            self.get_clipboard().set(text.strip())

    ### callbacks ###

    @Gtk.Template.Callback('closed')
    def _terminal_closed(self, dialog):
        terminal = self.placeholder.get_child()
        self.placeholder.set_child(None)
        config.set('stashed-terminal', terminal)
