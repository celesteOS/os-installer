# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .buttons import TerminalButton


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/failed.ui')
class FailedPage(Gtk.Box):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
