# SPDX-License-Identifier: GPL-3.0-or-later

from typing import NamedTuple

from gi.repository import Gdk

from .config import config
from .preloadable import Preloadable


class Desktop(NamedTuple):
    name: str
    description: str
    texture: Gdk.Texture
    keyword: str


class DesktopProvider(Preloadable):
    def __init__(self):
        super().__init__(self._get_desktops)

    def _get_desktops(self):
        self.desktops: list = []
        for entry in config.get('desktop'):
            if not set(entry).issuperset(['name', 'keyword', 'image_path']):
                print(f'Desktop choice not correctly configured: {entry}')
                continue
            description = entry.get('description', '')
            image_path = config.base_path / entry['image_path']

            if image_path.exists():
                texture = Gdk.Texture.new_from_filename(str(image_path))
            else:
                print(f'Could not find desktop image "{image_path}"')
                texture = None
            desktop = Desktop(entry['name'], description,
                              texture, entry['keyword'])
            self.desktops.append(desktop)

    ### public methods ###

    def get_desktops(self):
        self.assert_preloaded()
        return self.desktops


desktop_provider = DesktopProvider()
