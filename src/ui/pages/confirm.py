# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .config import config
from .device_rows import DeviceSummaryRow
from .functions import reset_model


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/confirm.ui')
class ConfirmPage(Gtk.Box):
    __gtype_name__ = __qualname__

    list = Gtk.Template.Child()
    model = Gio.ListStore()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.list.bind_model(self.model, lambda d: DeviceSummaryRow(d))
        config.subscribe('chosen_device', self._update_disk_row)

    ### callbacks ###

    def _update_disk_row(self, disk):
        if disk == None:
            if not config.get('test_mode'):
                print('Critical: Disk was not set before confirm page')
        else:
            reset_model(self.model, [disk])
