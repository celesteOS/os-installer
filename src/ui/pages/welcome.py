# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from gi.repository import Gtk

from .config import config
from .welcome_provider import welcome_provider


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/welcome.ui')
class WelcomePage(Gtk.Box):
    __gtype_name__ = __qualname__
    image = 'weather-clear-symbolic'

    description = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        welcome_provider.assert_preloaded()

        welcome = config.get('welcome_page')
        language_code = config.get('language')[0]

        if (text_key := f'text_{language_code}') in welcome:
            text = welcome[text_key]
        elif welcome['text']:
            text = welcome['text']
        else:
            text = self.description.get_label()
            text = text.format(config.get('distribution_name'))
        self.description.set_label(text)
