# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config
from .format_provider import get_current_formats
from .global_state import global_state
from .timezone_provider import get_current_timezone
from .system_calls import set_system_formats
from .page import Page


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/locale.ui')
class LocalePage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'globe-symbolic'

    formats_label = Gtk.Template.Child()
    timezone_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        if not config.has('formats_ui'):
            locale, name = get_current_formats()
            set_system_formats(locale, name)

        if not config.has('timezone'):
            timezone = get_current_timezone()
            config.set('timezone', timezone)

        self._subscribe('formats_ui', self._update_formats)
        self._subscribe('timezone', self._update_timezone)

    ### callbacks ###

    def _update_formats(self, formats):
        self.formats_label.set_label(formats)

    def _update_timezone(self, timezone):
        self.timezone_label.set_label(timezone)

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self)

    @Gtk.Template.Callback('overview_row_activated')
    def _overview_row_activated(self, list_box, row):
        global_state.navigate_to_page(row.get_name())
