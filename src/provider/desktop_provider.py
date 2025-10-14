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
            if not set(entry).issuperset(['name', 'keyword']):
                print(f'Desktop choice not correctly configured: {entry}')
                continue
            description = entry.get('description', '')
            texture = self._get_texture(entry)
            self.desktops.append(Desktop(entry['name'], description,
                                 texture, entry['keyword']))

    def _get_texture(self, entry):
        if 'image_path' in entry:
            image_path = config.base_path / entry['image_path']
            if image_path.exists():
                return Gdk.Texture.new_from_filename(str(image_path))
            else:
                print(f'Could not find desktop image "{image_path}"')
        return None

    ### public methods ###

    def get_desktops(self):
        self.assert_preloaded()
        return self.desktops


desktop_provider = DesktopProvider()
