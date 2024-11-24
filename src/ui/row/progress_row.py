# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/progress_row.ui')
class ProgressRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    def __init__(self, label, additional_info=None, **kwargs):
        super().__init__(**kwargs)

        self.set_title(label)
        self.info = additional_info
