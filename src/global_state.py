# SPDX-License-Identifier: GPL-3.0-or-later

import traceback


class GlobalState:
    def _uninitialized(self):
        print('Window method called before initialization.')
        traceback.print_stack()

    def advance(self, *args):
        self._uninitialized()

    def retranslate_pages(self, *args):
        self._uninitialized()

    def navigate_to_page(self, *args):
        self._uninitialized()


global_state = GlobalState()
