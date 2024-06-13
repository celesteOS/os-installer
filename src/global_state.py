# SPDX-License-Identifier: GPL-3.0-or-later

from concurrent.futures import ThreadPoolExecutor
import traceback
from .config import config


class GlobalState:
    demo_mode = False
    test_mode = False
    installation_running = False

    thread_pool = ThreadPoolExecutor()  # for futures

    def __init__(self):
        self.set_config('disk_name', 'Test Dummy')

    def _uninitialized(self):
        print('Window method called before initialization.')
        traceback.print_stack()

    def get_config(self, setting):
        return config.get(setting)

    def set_config(self, setting, value):
        config.set(setting, value)

    def advance(self, *args):
        self._uninitialized()

    def retranslate_pages(self, *args):
        self._uninitialized()

    def navigate_to_page(self, *args):
        self._uninitialized()

    def reload_title_image(self, *args):
        self._uninitialized()

    def send_notification(self, *args):
        self._uninitialized()

global_state = GlobalState()
