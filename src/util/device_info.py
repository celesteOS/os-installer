
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GObject


class DeviceInfo(GObject.Object):
    __gtype_name__ = __qualname__

    def __init__(self, name, size, size_text, device_path, is_efi=False):
        self._name: str = name
        self._size_text: str = size_text
        self._device_path: str = device_path
        self.size_number: int = size
        self.is_efi: bool = is_efi
        self.efi_partition: str = ''
        super().__init__()

    @GObject.Property(type=str)
    def device_path(self):
        return self._device_path

    @GObject.Property(type=str)
    def name(self):
        return self._name

    @GObject.Property(type=str)
    def size(self):
        return self._size_text


class Disk(DeviceInfo):
    partitions: list = []

    def __init__(self, name, size, size_text, device_path, partitions):
        super().__init__(name, size, size_text, device_path)

        if partitions:
            efis = [partition for partition in partitions if partition.is_efi]
            self.efi_partition = efis[0].name if len(efis) > 0 else ''
            for partition in partitions:
                partition.efi_partition = self.efi_partition
            self.partitions = partitions
