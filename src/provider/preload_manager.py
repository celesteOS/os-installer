# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread

from .language_provider import language_provider


class PreloadManager:
    def __init__(self):
        self.thread = Thread(target=self._preload)

    def _preload(self):
        language_provider.preload()
        language_provider.assert_preloaded()

    ### public methods ###

    def start(self):
        self.thread.start()


preload_manager = PreloadManager()
