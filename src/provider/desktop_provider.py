# SPDX-License-Identifier: GPL-3.0-or-later

from typing import NamedTuple

from .config import config
from .preloadable import Preloadable


class Desktop(NamedTuple):
    name: str
    description: str
    image_path: str
    keyword: str


class DesktopProvider(Preloadable):
    def __init__(self):
        Preloadable.__init__(self, self._get_desktops)

    def _get_desktops(self):
        self.desktops: list = []
        for entry in config.get('desktop'):
            if not set(entry).issuperset(['name', 'keyword', 'image_path']):
                print(f'Desktop choice not correctly configured: {entry}')
                continue
            description = entry['description'] if 'description' in entry else ''
            desktop = Desktop(entry['name'], description,
                              entry['image_path'], entry['keyword'])
            self.desktops.append(desktop)

    ### public methods ###

    def get_desktops(self):
        self.assert_preloaded()
        return self.desktops


desktop_provider = DesktopProvider()
