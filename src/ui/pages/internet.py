# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock

from gi.repository import Gtk

from .config import config
from .global_state import global_state
from .page import Page
from .system_calls import open_wifi_settings, start_system_timesync


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/internet.ui')
class InternetPage(Gtk.Stack, Page):
    __gtype_name__ = __qualname__
    image = 'network-wireless-disabled-symbolic'

    def __init__(self, **kwargs):
        Gtk.Stack.__init__(self, **kwargs)

        self.update_lock = Lock()

        self.initial_load = True
        config.subscribe('internet_connection', self._connection_state_changed)
        self.initial_load = False

    ### callbacks ###

    @Gtk.Template.Callback('clicked_settings_button')
    def _clicked_settings_button(self, button):
        open_wifi_settings()

    def _connection_state_changed(self, connected):
        with self.update_lock:
            if connected:
                self.set_visible_child_name('connected')
                self.image = 'network-wireless-symbolic'
                start_system_timesync()
                if self.initial_load:
                    config.set('page_navigation', 'pass')
                else:
                    global_state.advance(self)
            else:
                self.set_visible_child_name('not-connected')
                self.image = 'network-wireless-disabled-symbolic'

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        global_state.advance(self)
