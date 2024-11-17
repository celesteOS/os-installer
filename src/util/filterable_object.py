# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GObject


class FilterableObject(GObject.Object):
    __gtype_name__ = __qualname__

    def __init__(self, name, id, search_string):
        super().__init__()

        self.name: str = name
        self.id: str = id
        self.search_string = search_string

    @GObject.Property(type=str)
    def title(self):
        return self.name
