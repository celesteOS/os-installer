# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .system_calls import open_internet_search


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/failed.ui')
class FailedPage(Gtk.Box):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    ### callbacks ###

    @Gtk.Template.Callback('search_button_clicked')
    def _search_button_clicked(self, button):
        open_internet_search()
