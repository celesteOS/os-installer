# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock, Thread

from gi.repository import Gtk

from .buttons import ContinueButton
from .config import config
from .system_calls import start_system_timesync
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/internet.ui')
class InternetPage(Gtk.Stack):
    __gtype_name__ = __qualname__
    image = 'network-wireless-disabled-symbolic'

    no_connection_label = Gtk.Template.Child()
    settings_button = Gtk.Template.Child()
    yes_connection_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.no_connection_label, self.settings_button,
                          self.yes_connection_label)

        self.update_lock = Lock()
        self.has_advanced = False

        config.subscribe('internet_connection', self._connection_state_changed)

    ### callbacks ###

    def _connection_state_changed(self, connected):
        with self.update_lock:
            if connected:
                self.set_visible_child_name('connected')
                config.set('internet_page_image',
                           'network-wireless-symbolic')
                start_system_timesync()
                if not self.has_advanced:
                    self.has_advanced = True
                    Thread(target=config.set_next_page, args=[self]).start()
            else:
                self.set_visible_child_name('not-connected')
                config.set('internet_page_image',
                           'network-wireless-disabled-symbolic')
