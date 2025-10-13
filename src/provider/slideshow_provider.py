# SPDX-License-Identifier: GPL-3.0-or-later

from typing import NamedTuple

from gi.repository import Gdk

from .config import config
from .preloadable import Preloadable


class Slide(NamedTuple):
    image: Gdk.Texture
    duration: float


class SlideshowProvider(Preloadable):
    def __init__(self):
        super().__init__(self._load_slideshow)

    def _load_slideshow(self):
        entries = config.get('install_slideshow')
        self.slideshow = []
        for entry in entries:
            if 'image_path' not in entry:
                print(f'Ignoring slideshow entry due to missing image: "{entry}"')
                continue

            image_path = config.base_path / entry.get('image_path')

            if not image_path.exists():
                print(f'Could not find slideshow image "{image_path}"')
            else:
                image = Gdk.Texture.new_from_filename(str(image_path))
                seconds = entry.get('seconds', 5)
                self.slideshow.append(Slide(image, seconds))

    ### public methods ###

    def get_slideshow(self):
        self.assert_preloaded()
        return self.slideshow


slideshow_provider = SlideshowProvider()
