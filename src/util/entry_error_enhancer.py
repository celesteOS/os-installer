# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk


class EntryErrorEnhancer():
    def __init__(self, row, condition):
        self.row = row
        self.condition = condition
        self.error = None

        self.update_row(self.row.get_text())

    def __bool__(self):
        return self.ok

    def update_row(self, text):
        self.empty = len(text) == 0
        self.ok = self.condition(text)

        if self.error and (self.empty or self.ok):
            self.row.remove_css_class('error')
            self.row.remove(self.error)
            del self.error
            self.error = None
        elif not self.error and not self.empty and not self.ok:
            self.row.add_css_class('error')
            self.error = Gtk.Image.new_from_icon_name(
                'dialog-warning-symbolic')
            self.row.add_suffix(self.error)
        return bool(self)
