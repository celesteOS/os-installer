# SPDX-License-Identifier: GPL-3.0-or-later

import gettext
import locale


from .config import config


class Translator:
    def __init__(self, localedir):
        self.config_localedir = '/etc/os-installer/po/'
        self.localedir = localedir
        self.translation_cache = {}

        self._setup_module()

        config.subscribe('language_chosen',
                         lambda info: self._setup_language(info.code))

    def _setup_module(self):
        for module in [gettext, locale]:
            module.bindtextdomain('os-installer', self.localedir)
            module.bindtextdomain('os-installer-config', self.config_localedir)
            module.textdomain('os-installer')
        gettext.install('os-installer')

    def _setup_language(self, code):
        self.default = self.get_language(code)
        try:
            self.config = gettext.translation(
                'os-installer-config', self.config_localedir, [code])
        except FileNotFoundError:
            self.config = self.default
        self.default.install()

    def get_language(self, code):
        if code in self.translation_cache:
            # reuse existing translation
            return self.translation_cache[code]

        try:
            translation = gettext.translation(
                'os-installer', self.localedir, [code])
            self.translation_cache[code] = translation
            return translation
        except FileNotFoundError:
            return self.default


translator = None


def initialize_translator(localedir):
    global translator
    translator = Translator(localedir)


def config_gettext(text):
    return translator.config.gettext(text)


def language_gettext(language, text):
    return translator.get_language(language).gettext(text)
