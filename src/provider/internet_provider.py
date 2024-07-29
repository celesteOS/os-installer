# SPDX-License-Identifier: GPL-3.0-or-later

import time
from threading import Thread
from urllib.request import urlopen

from .config import config
from .global_state import global_state


def check_connection(url):
    try:
        urlopen(url, timeout=50)
        return True
    except:
        return False


class InternetProvider():
    def __init__(self):
        self.url = config.get('internet_checker_url')

        # start internet connection checking
        self._start_connection_checker()
        self.thread = Thread(target=self._poll, daemon=True)
        self.thread.start()

    def _start_connection_checker(self):
        self.connection_checker = global_state.thread_pool.submit(
            check_connection, url=self.url)

    def _poll(self):
        connected = False
        while not connected:
            if not self.connection_checker.done():
                time.sleep(0.5)  # wait 500ms
            else:
                connected = self.connection_checker.result()
                config.set('internet_connection', connected)

                if not connected:
                    # restart checker
                    self._start_connection_checker()


internet_provider = InternetProvider()
