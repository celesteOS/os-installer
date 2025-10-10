# SPDX-License-Identifier: GPL-3.0-or-later

import os

from gi.repository import Gdk

from .config import config
from .preloadable import Preloadable


class WelcomeProvider(Preloadable):
    def __init__(self):
        super().__init__(self._load_image)

    def _load_image(self):
        welcome = config.get('welcome_page')

        page_image = 'weather-clear-symbolic'
        if welcome and (logo := welcome['logo']):
            if os.path.exists(logo):
                page_image = Gdk.Texture.new_from_filename(logo)
            else:
                print(f'Could not find welcome logo "{logo}"')

        config.set('welcome_page_image', page_image)


welcome_provider = WelcomeProvider()
