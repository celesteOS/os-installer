# SPDX-License-Identifier: GPL-3.0-or-later

from random import getrandbits
from threading import Lock

from gi.repository import Gio, Gtk

from .disk_provider import get_disk_provider
from .global_state import global_state
from .page import Page
from .system_calls import is_booted_with_uefi
from .widgets import reset_model, DeviceRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/partition.ui')
class PartitionPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    no_disk_image_name = 'no-disk-symbolic'
    default_image_name = 'drive-harddisk-system-symbolic'
    image = default_image_name
    can_reload = True

    disk_label = Gtk.Template.Child()
    disk_size = Gtk.Template.Child()

    whole_disk_row = Gtk.Template.Child()
    partition_stack = Gtk.Template.Child()
    partition_list = Gtk.Template.Child()

    disk_list_model = Gio.ListStore()
    partition_list_model = Gio.ListStore()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.disk_provider = get_disk_provider()
        self.disk = None
        self.lock = Lock()
        self.minimum_disk_size = global_state.get_config('minimum_disk_size')

        # models
        self.partition_list.bind_model(
            self.partition_list_model, self._create_device_row)

    def _create_device_row(self, info):
        if info.size >= self.minimum_disk_size:
            return DeviceRow(info)
        else:
            required_size_str = self.disk_provider.disk_size_to_str(
                self.minimum_disk_size)
            return DeviceRow(info, required_size_str)

    def disk_exists(self):
        if global_state.demo_mode:
            return True
        elif global_state.test_mode:
            # claim disk existance in about 75% of cases
            claim_existance = getrandbits(2) != 3
            if not claim_existance:
                print('test-mode: randomly chose that disk does not exist anymore')
            return claim_existance
        else:
            return self.disk_provider.disk_exists(self.disk)

    def _setup_partition_list(self):
        self.disk = global_state.get_config('selected_disk')

        if not self.disk_exists():
            return "load_prev"

        if len(self.disk.partitions) == 0:
            reset_model(self.partition_list_model, [])
            self.partition_stack.set_visible_child_name("no-partitions")
        elif is_booted_with_uefi() and self.disk.efi_partition is None:
            self.partition_stack.set_visible_child_name("no-boot-partition")
        else:
            reset_model(self.partition_list_model, self.disk.partitions)
            self.partition_stack.set_visible_child_name("available")

        # set disk info
        self.disk_label.set_label(self.disk.name)
        self.whole_disk_row.set_subtitle(self.disk.device_path)
        self.disk_size.set_label(self.disk.size_text)

    def _store_device_info(self, info):
        global_state.set_config('disk_name', info.name)
        global_state.set_config('disk_device_path', info.device_path)
        global_state.set_config('disk_is_partition',
                                not type(info) == type(self.disk))
        global_state.set_config('disk_efi_partition', self.disk.efi_partition)

    ### callbacks ###

    @Gtk.Template.Callback('use_partition')
    def _use_partition(self, list_box, row):
        info = row.info
        if not info.name:
            info.name = row.get_title()
        self._store_device_info(info)
        global_state.advance(self)

    @Gtk.Template.Callback('use_whole_disk')
    def _use_whole_disk(self, list_box, row):
        self._store_device_info(self.disk)
        global_state.advance(self)

    ### public methods ###

    def load(self):
        with self.lock:
            response = self._setup_partition_list()
        self.loaded = True
        return response
