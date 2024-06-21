# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock

from gi.repository import Gtk

from .config import config
from .global_state import global_state
from .internet_provider import internet_provider
from .page import Page
from .system_calls import open_wifi_settings, start_system_timesync


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/internet.ui')
class InternetPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'network-wireless-disabled-symbolic'

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.connected = False
        self.connected_lock = Lock()

        # setup connected callback
        internet_provider.set_connected_callback(self._on_connected)

    ### callbacks ###

    @Gtk.Template.Callback('clicked_settings_button')
    def _clicked_settings_button(self, button):
        open_wifi_settings()

    def _on_connected(self):
        with self.connected_lock:
            self.image = 'network-wireless-symbolic'
            self.connected = True
            global_state.reload_title_image()
            start_system_timesync()

        # do not hold lock, could cause deadlock with simultaneous load()
        global_state.advance(self)

    ### public methods ###

    def load(self):
        with self.connected_lock:
            if self.connected:
                return "pass"
