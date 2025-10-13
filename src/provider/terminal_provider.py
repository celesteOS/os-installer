# SPDX-License-Identifier: GPL-3.0-or-later

import ctypes

from .config import config
from .preloadable import Preloadable


class TerminalProvider(Preloadable):
    def __init__(self):
        super().__init__(self._initialize_terminal, 'terminal-placeholder')

    def _initialize_terminal(self, terminal_placeholder):
        self.terminal_placeholder = terminal_placeholder
        self.terminal = self.terminal_placeholder.get_child()
        self.stashed = True
        config.subscribe('logged-error', self._log_error, delayed=True)

        # add empty line on top for margin
        new_line = (ctypes.c_char * 1).from_buffer_copy(b'\n')
        self.terminal.feed(new_line)

    def _log_error(self, error):
        print(error)
        if self.stashed and error:
           self.terminal.feed(str.encode(f'{error}\n\r'))

    def set_pty(self, pty):
        self.assert_preloaded()
        self.terminal.set_pty(pty)

    def steal(self):
        self.assert_preloaded()
        if self.stashed:
            self.terminal_placeholder.set_child(None)
        else:
            print('Internal error: Tried taking terminal while not stashed')
        self.stashed = False
        return self.terminal

    def stash(self):
        self.assert_preloaded()
        self.terminal_placeholder.set_child(self.terminal)
        self.stashed = True


terminal_provider = TerminalProvider()
