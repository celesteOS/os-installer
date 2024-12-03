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
            if not 'image_path' in entry:
                print(f'Ignoring faulty slideshow entry "{entry}"')
                continue
            image = Gdk.Texture.new_from_filename(entry['image_path'])
            seconds = entry.get('seconds', 5)
            self.slideshow.append(Slide(image, seconds))

    ### public methods ###

    def get_slideshow(self):
        self.assert_preloaded()
        return self.slideshow


slideshow_provider = SlideshowProvider()
