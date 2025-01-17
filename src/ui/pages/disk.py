# SPDX-License-Identifier: GPL-3.0-or-later

import os

from gi.repository import Gio, Gtk

from .config import config
from .device_info import DeviceInfo, Disk
from .device_rows import DeviceChoiceRow, DeviceRow, DeviceTooSmallRow, NoEfiPartitionRow
from .disk_provider import disk_provider
from .functions import reset_model
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/disk.ui')
class DiskPage(Gtk.Stack):
    __gtype_name__ = __qualname__

    disk_list = Gtk.Template.Child()
    disks_button = Gtk.Template.Child()
    no_disks_page = Gtk.Template.Child()
    reload_button = Gtk.Template.Child()

    disk_list_model = Gio.ListStore()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.disks_button, self.no_disks_page,
                          self.reload_button)

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

    def _create_device_row(self, device: DeviceInfo):
        if not self._is_big_enough(device.size_number):
            return DeviceTooSmallRow(device)
        if not self.partition_ok or not device.partitions:
            return DeviceRow(device)

        expander_row = DeviceChoiceRow(device, self._row_activated)

        can_use_partitions = True
        is_booted_with_uefi = os.path.isdir("/sys/firmware/efi/efivars")
        if is_booted_with_uefi and device.efi_partition is None:
            expander_row.add_row(NoEfiPartitionRow())
            can_use_partitions = False

        for partition in device.partitions:
            if self._is_big_enough(partition.size_number):
                row = DeviceRow(partition)
                row.connect('activated', self._row_activated)
                row.set_sensitive(can_use_partitions and not partition.is_efi)
                expander_row.add_row(row)
            else:
                expander_row.add_row(DeviceTooSmallRow(partition))
        return expander_row

    ### callbacks ###

    @Gtk.Template.Callback('disk_selected')
    def _disk_selected(self, list_box, row):
        self._row_activated(row)

    def _row_activated(self, row):
        config.set('chosen_device', row.device)
        config.set('disk_is_partition', not type(row.device) == Disk)
        config.set('disk_efi_partition', row.device.efi_partition)
        config.set_next_page(self)
