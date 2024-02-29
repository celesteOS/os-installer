# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Thread

from .choices_provider import choices_provider
from .disk_provider import disk_provider
from .language_provider import language_provider


class PreloadManager:
    def __init__(self):
        self.thread = Thread(target=self._preload)

    def _preload(self):
        language_provider.preload()
        language_provider.assert_preloaded()

        disk_provider.preload()
        disk_provider.assert_preloaded()

        choices_provider.preload()
        choices_provider.assert_preloaded()

    ### public methods ###

    def start(self):
        self.thread.start()


preload_manager = PreloadManager()
