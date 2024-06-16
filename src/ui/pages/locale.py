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

    ### callbacks ###

    @Gtk.Template.Callback('continue')
    def _continue(self, button):
        global_state.advance(self)

    @Gtk.Template.Callback('overview_row_activated')
    def _overview_row_activated(self, list_box, row):
        global_state.navigate_to_page(row.get_name())

    ### public methods ###

    def load(self):
        formats = config.get('formats_ui')
        if not formats:
            locale, name = get_current_formats()
            set_system_formats(locale, name)
            formats = config.set('formats_ui', name)
        self.formats_label.set_label(formats)

        timezone = config.get('timezone')
        if not timezone:
            timezone = get_current_timezone()
            config.set('timezone', timezone)
        self.timezone_label.set_label(timezone)
