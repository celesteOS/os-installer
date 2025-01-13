# SPDX-License-Identifier: GPL-3.0-or-later

import ctypes

from gi.repository import Adw, Gtk, Vte

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/terminal_dialog.ui')
class TerminalDialog(Adw.Dialog):
    __gtype_name__ = __qualname__

    placeholder = Gtk.Template.Child()

    def __init__(self, terminal, **kwargs):
        super().__init__(**kwargs)

        if not terminal:
            # create a new terminal and use existing PTY for it
            terminal = Vte.Terminal()
            terminal.set_allow_hyperlink(True)
            terminal.set_input_enabled(False)
            terminal.set_scroll_on_output(True)
            terminal.set_scrollback_lines(10000)

            # add empty line on top for margin
            new_line = (ctypes.c_char * 1).from_buffer_copy(b'\n')
            terminal.feed(new_line)

            pty = config.steal('script_pty')
            terminal.set_pty(pty)
        self.placeholder.set_child(terminal)

    ### callbacks ###

    @Gtk.Template.Callback('closed')
    def _terminal_closed(self, dialog):
        terminal = self.placeholder.get_child()
        self.placeholder.set_child(None)
        config.set('stashed-terminal', terminal)
