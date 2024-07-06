# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock

from gi.repository import Gtk

from .config import config
from .global_state import global_state
from .internet_provider import internet_provider
from .page import Page
from .system_calls import open_wifi_settings, start_system_timesync


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/internet.ui')
class InternetPage(Gtk.Stack, Page):
    __gtype_name__ = __qualname__
    image = 'network-wireless-disabled-symbolic'

    def __init__(self, **kwargs):
        Gtk.Stack.__init__(self, **kwargs)

        self.connected = False
        self.connected_lock = Lock()

        self.set_visible_child_name('not-connected')

        # setup connected callback
        internet_provider.set_connected_callback(self._on_connected)

        with self.connected_lock:
            if self.connected:
                config.set('page_navigation', 'pass')

    ### callbacks ###

    @Gtk.Template.Callback('clicked_settings_button')
    def _clicked_settings_button(self, button):
        open_wifi_settings()

    def _on_connected(self):
        with self.connected_lock:
            self.set_visible_child_name('connected')
            self.image = 'network-wireless-symbolic'
            self.connected = True
            start_system_timesync()

        # do not hold lock, could cause deadlock with simultaneous load()
        global_state.advance(self)

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        global_state.advance(self)
