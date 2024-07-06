# SPDX-License-Identifier: GPL-3.0-or-later

from concurrent.futures import ThreadPoolExecutor
import traceback


class GlobalState:
    thread_pool = ThreadPoolExecutor()  # for futures

    def _uninitialized(self):
        print('Window method called before initialization.')
        traceback.print_stack()

    def advance(self, *args):
        self._uninitialized()

    def retranslate_pages(self, *args):
        self._uninitialized()

    def navigate_to_page(self, *args):
        self._uninitialized()

    def send_notification(self, *args):
        self._uninitialized()

global_state = GlobalState()
