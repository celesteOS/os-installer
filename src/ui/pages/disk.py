# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gio, Gtk

from .config import config
from .disk_provider import DeviceInfo, get_disk_provider
from .global_state import global_state
from .installation_scripting import installation_scripting
from .page import Page
from .system_calls import is_booted_with_uefi, open_disks
from .widgets import reset_model, DeviceRow


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/disk.ui')
class DiskPage(Gtk.Stack, Page):
    __gtype_name__ = __qualname__
    no_disk_image_name = 'no-disk-symbolic'
    default_image_name = 'drive-harddisk-system-symbolic'
    image = default_image_name

    disk_list = Gtk.Template.Child()

    disk_list_model = Gio.ListStore()

    current_disk = None

    def __init__(self, **kwargs):
        Gtk.Stack.__init__(self, **kwargs)

        self.minimum_disk_size = config.get('minimum_disk_size')
        self.disk_provider = get_disk_provider()

        # models
        self.disk_list.bind_model(self.disk_list_model, self._create_device_row)

        if disks := self.disk_provider.get_disks():
            reset_model(self.disk_list_model, disks)
            self.set_visible_child_name('disks')
            self.image = self.default_image_name
        else:
            self.set_visible_child_name('no-disks')
            self.image = self.no_disk_image_name

        installation_scripting.can_run_prepare()

    def _create_device_row(self, info: DeviceInfo):
        if info.size >= self.minimum_disk_size:
            return DeviceRow(info)
        else:
            required_size_str = self.disk_provider.disk_size_to_str(self.minimum_disk_size)
            return DeviceRow(info, required_size_str)

    ### callbacks ###

    @Gtk.Template.Callback('clicked_disks_button')
    def _clicked_disks_button(self, button):
        open_disks()

    @Gtk.Template.Callback('disk_selected')
    def _disk_selected(self, list_box, row):
        config.set('selected_disk', row.info)
        global_state.advance(self)
