# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/device_choice_row.ui')
class DeviceChoiceRow(Adw.ExpanderRow):
    __gtype_name__ = __qualname__

    size_label = Gtk.Template.Child()
    whole_disk_row = Gtk.Template.Child()

    def __init__(self, info, callback, **kwargs):
        super().__init__(**kwargs)

        self.info = info
        self.size_label.set_label(info.size_text)
        self.set_title(info.name)
        self.set_subtitle(info.device_path)

        self.callback = callback

    @Gtk.Template.Callback('use_whole_disk')
    def _use_whole_disk(self, row):
        self.callback(self)


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/device_row.ui')
class DeviceRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    size_label = Gtk.Template.Child()

    def __init__(self, info, **kwargs):
        super().__init__(**kwargs)

        self.info = info
        self.size_label.set_label(info.size_text)
        self.set_title(info.name)
        self.set_subtitle(info.device_path)


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/device_too_small_row.ui')
class DeviceTooSmallRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    size_label = Gtk.Template.Child()
    too_small_label = Gtk.Template.Child()

    def __init__(self, info, **kwargs):
        super().__init__(**kwargs)

        self.size_label.set_label(info.size_text)
        self.set_title(info.name)
        self.set_subtitle(info.device_path)

        smol = self.too_small_label.get_label()
        required_size_str = config.get('min_disk_size_str')
        self.too_small_label.set_label(smol.format(required_size_str))


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/no_efi_partition_row.ui')
class NoEfiPartitionRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
