# SPDX-License-Identifier: GPL-3.0-or-later

from random import getrandbits

from gi.repository import GLib, GObject

from .config import config
from .device_info import DeviceInfo, Disk
from .preloadable import Preloadable


class DiskProvider(Preloadable):

    EFI_PARTITION_GUID = 'C12A7328-F81F-11D2-BA4B-00A0C93EC93B'
    EFI_PARTITON_FLAGS = None

    def __init__(self):
        super().__init__(self._init_client)

    def _init_client(self):
        min_disk_size = config.get('disk')['min_size']

        # avoids initializing udisks client in demo mode
        self.use_dummy_implementation = config.is_demo()
        if self.use_dummy_implementation:
            # fake it till you make it
            min_disk_size_str = f'{min_disk_size / 1000000000:.1f} GB'
            config.set('min_disk_size_str', min_disk_size_str)
            return

        import gi                            # noqa: E402
        gi.require_version('UDisks', '2.0')  # noqa: E402
        from gi.repository import UDisks
        self.EFI_PARTITON_FLAGS = UDisks.PartitionTypeInfoFlags.SYSTEM.numerator
        self.udisks_client = UDisks.Client.new_sync()

        config.set('min_disk_size_str', self._disk_size_to_str(min_disk_size))

    def _disk_size_to_str(self, size):
        return self.udisks_client.get_size_for_display(size, False, False)

    def _get_partition_info(self, partition, block):
        partition_label = block.props.id_label.strip()
        if not partition_label:
            # Translators: Fallback name for partitions that don't have a name
            name = _("Unnamed Partition")
        else:
            # Translators: Squiggly brackets are replaced with partition name
            partition_str = _("{} (Partition)")
            name = partition_str.format(partition_label)

        return DeviceInfo(
            name=name,
            size=block.props.size,
            size_text=self._disk_size_to_str(block.props.size),
            device_path=block.props.device,
            is_efi=partition.props.type.upper() == self.EFI_PARTITION_GUID)

    def _get_partitions(self, partition_table):
        if not partition_table:
            return None

        partitions = []
        for partition_name in partition_table.props.partitions:
            partition_object = self.udisks_client.get_object(partition_name)
            if not partition_object:
                continue
            block = partition_object.get_block()
            partition = partition_object.get_partition()
            if block and partition:
                partitions.append(self._get_partition_info(partition, block))
            else:
                print('Unhandled partiton in partition table, ignoring.')

        return partitions

    def _get_disk_info(self, block, drive, partition_table):
        if not (name := (f'{drive.props.vendor} {drive.props.model}'.strip())):
            # Translators: Fallback name for partitions that don't have a name
            name = _("Unnamed Disk")
        return Disk(
            name=name,
            size=block.props.size,
            size_text=self._disk_size_to_str(block.props.size),
            device_path=block.props.device,
            partitions=self._get_partitions(partition_table))

    def _get_dummy_disks(self):
        return [
            Disk("Dummy", 10000, "10 KB", "/dev/null",
                 [DeviceInfo("Too small partiton", 1000, "1 KB", "/dev/00null")]),
            Disk("Totally real device", 100000000000, "100 GB", "/dev/sda", [
                DeviceInfo("EFI", 200000000, "2 GB", "/dev/sda_efi", True),
                DeviceInfo("Previous Installation", 20000000000, "40 GB",
                           "/dev/sda_yes"),
                DeviceInfo(_("Unnamed Partition"), 20000000000, "30 GB", "/dev/sda_unnamed"),
                DeviceInfo(_("Unnamed Partition"), 20000000000, "20 GB", "/dev/sda_unnamed2"),
                DeviceInfo("Swap", 20000000000, "8 GB", '/dev/sda_swap'),
            ]),
            Disk("VERY BIG DISK", 1000000000000000, "1000 TB",
                 "/dev/sdb_very_big", []),
        ]

    ### public methods ###

    def disk_exists(self, dev_info: DeviceInfo):
        self.assert_preloaded()

        if self.use_dummy_implementation:
            return True

        # check against all available devices
        dummy_var = GLib.Variant('a{sv}', None)
        manager = self.udisks_client.get_manager()
        devices = manager.call_get_block_devices_sync(dummy_var, None)
        for device in devices:
            if ((udisks_object := self.udisks_client.get_object(device)) and
                (block := udisks_object.get_block()) and
                    block.props.device == dev_info.device_path):
                return True

        return False

    def get_disks(self):
        self.assert_preloaded()

        if self.use_dummy_implementation:
            return self._get_dummy_disks()

        if config.is_test() and getrandbits(3) == 7:
            print("test-mode: randomly chose that no disks are available")
            return []

        # get available devices
        dummy_var = GLib.Variant('a{sv}', None)
        manager = self.udisks_client.get_manager()
        devices = manager.call_get_block_devices_sync(dummy_var, None)

        # get device information
        disks = []
        for device in devices:
            udisks_object = self.udisks_client.get_object(device)
            if not udisks_object:
                continue

            # skip partitions
            partition = udisks_object.get_partition()
            if partition:
                continue

            block = udisks_object.get_block()
            if not block:
                continue

            partition_table = udisks_object.get_partition_table()
            drive = self.udisks_client.get_drive_for_block(block)
            if drive and not drive.props.optical:
                disk_info = self._get_disk_info(block, drive, partition_table)
                disks.append(disk_info)

        return disks


disk_provider = DiskProvider()
