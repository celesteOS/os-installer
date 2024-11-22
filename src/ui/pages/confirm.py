# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/confirm.ui')
class ConfirmPage(Gtk.Box):
    __gtype_name__ = __qualname__

    disk_row = Gtk.Template.Child()
    size_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        config.subscribe('chosen_device', self._update_disk_row)

    ### callbacks ###

    def _update_disk_row(self, disk):
        if disk == None:
            if not config.get('test_mode'):
                print('Critical: Disk was not set before confirm page')
            return
        self.disk_row.set_title(disk.name)
        self.disk_row.set_subtitle(disk.device_path)
        self.size_label.set_label(disk.size_text)

    @Gtk.Template.Callback('confirmed')
    def _confirmed(self, button):
        config.set_next_page(self)
