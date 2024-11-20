# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .config import config
from .disk_provider import DeviceInfo, Disk, disk_provider
from .system_calls import is_booted_with_uefi, open_disks
from .widgets import reset_model, DeviceChoiceRow, DeviceRow, DeviceTooSmallRow, NoEfiPartitionRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/disk.ui')
class DiskPage(Gtk.Stack):
    __gtype_name__ = __qualname__

    disk_list = Gtk.Template.Child()

    disk_list_model = Gio.ListStore()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        disk_conf = config.get('disk')
        self.minimum_disk_size = disk_conf['min_size']
        self.partition_ok = disk_conf['partition_ok']

        # models
        self.disk_list.bind_model(
            self.disk_list_model, self._create_device_row)

        if disks := disk_provider.get_disks():
            reset_model(self.disk_list_model, disks)
            self.set_visible_child_name('disks')
        else:
            self.set_visible_child_name('no-disks')

    def _is_big_enough(self, size):
        return size <= 0 or size >= self.minimum_disk_size

    def _create_device_row(self, info: DeviceInfo):
        if not self._is_big_enough(info.size):
            return DeviceTooSmallRow(info)
        if not self.partition_ok or not info.partitions:
            return DeviceRow(info)

        expander_row = DeviceChoiceRow(info, self._row_activated)

        can_use_partitions = True
        if is_booted_with_uefi() and info.efi_partition is None:
            expander_row.add_row(NoEfiPartitionRow())
            can_use_partitions = False

        for partition in info.partitions:
            if self._is_big_enough(partition.size):
                row = DeviceRow(partition)
                row.connect('activated', self._row_activated)
                row.set_sensitive(can_use_partitions and not partition.is_efi)
                expander_row.add_row(row)
            else:
                expander_row.add_row(DeviceTooSmallRow(partition))
        return expander_row

    ### callbacks ###

    @Gtk.Template.Callback('clicked_disks_button')
    def _clicked_disks_button(self, button):
        open_disks()

    @Gtk.Template.Callback('disk_selected')
    def _disk_selected(self, list_box, row):
        self._row_activated(row)

    def _row_activated(self, row):
        config.set('chosen_device', (row.info.device_path, row.info.name))
        config.set('disk_is_partition', not type(row.info) == Disk)
        config.set('disk_efi_partition', row.info.efi_partition)
        config.set_next_page(self)
