# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/summary_row.ui')
class SummaryRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
