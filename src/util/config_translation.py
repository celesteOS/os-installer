# SPDX-License-Identifier: GPL-3.0-or-later

from locale import textdomain


class ConfigTranslation():
    def __enter__(self):
        textdomain('os-installer-config')
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        textdomain('os-installer')


config_translation = ConfigTranslation()
