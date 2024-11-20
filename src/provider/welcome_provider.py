# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gdk

from .config import config
from .preloadable import Preloadable


class WelcomeProvider(Preloadable):
    def __init__(self):
        super().__init__(self._load_image)

    def _load_image(self):
        welcome = config.get('welcome_page')

        if welcome['logo']:
            texture = Gdk.Texture.new_from_filename(welcome['logo'])
            config.set('welcome_page_image', texture)


welcome_provider = WelcomeProvider()
