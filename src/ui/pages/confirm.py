# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .buttons import ConfirmButton
from .config import config
from .device_rows import DeviceSummaryRow
from .functions import reset_model
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/confirm.ui')
class ConfirmPage(Gtk.Box):
    __gtype_name__ = __qualname__

    explanation_label = Gtk.Template.Child()
    list = Gtk.Template.Child()
    model = Gio.ListStore()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.explanation_label)

        self.list.bind_model(self.model, lambda d: DeviceSummaryRow(d))
        config.subscribe('chosen_device', self._update_disk_row)

    ### callbacks ###

    def _update_disk_row(self, disk):
        if disk == None:
            if not config.is_test():
                print('Critical: Disk was not set before confirm page')
        else:
            reset_model(self.model, [disk])
