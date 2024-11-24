# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/summary_row.ui')
class SummaryRow(Gtk.ListBoxRow):
    __gtype_name__ = __qualname__

    icon = Gtk.Template.Child()
    name = Gtk.Template.Child()

    def __init__(self, choice, **kwargs):
        super().__init__(**kwargs)

        if choice.options:
            self.name.set_label(choice.state.display)
        else:
            self.name.set_label(choice.name)

        if choice.icon_path:
            self.icon.set_from_file(choice.icon_path)
        else:
            self.icon.set_from_icon_name(choice.icon_name)
