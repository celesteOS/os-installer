# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/locale.ui')
class LocalePage(Gtk.Box):
    __gtype_name__ = __qualname__

    formats_row = Gtk.Template.Child()
    timezone_row = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        config.subscribe('formats', self._update_formats)
        config.subscribe('timezone', self._update_timezone)

    ### callbacks ###

    def _update_formats(self, formats):
        self.formats_row.set_subtitle(formats[1])

    def _update_timezone(self, timezone):
        self.timezone_row.set_subtitle(timezone)

    @Gtk.Template.Callback('row_activated')
    def _row_activated(self, row):
        config.set('displayed-page', row.get_name())
