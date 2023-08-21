# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GObject


class SummaryEntry(GObject.GObject):
    __gtype_name__ = __qualname__

    def __init__(self, name, icon_path):
        super().__init__()

        self.name = name
        self.icon_path = icon_path
