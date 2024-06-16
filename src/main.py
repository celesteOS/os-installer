# SPDX-License-Identifier: GPL-3.0-or-later

import sys
from typing import Callable, NamedTuple

import gi
# set versions for all used submodules
gi.require_version('Gio', '2.0')           # noqa: E402
gi.require_version('GLib', '2.0')          # noqa: E402
gi.require_version('Gtk', '4.0')           # noqa: E402
gi.require_version('GnomeDesktop', '4.0')  # noqa: E402
gi.require_version('GWeather', '4.0')      # noqa: E402
gi.require_version('Adw', '1')             # noqa: E402
gi.require_version('Vte', '3.91')          # noqa: E402
from gi.repository import Adw, Gio, GLib, Gtk

# local, import order is important
from .config import config
from .global_state import global_state
from .preload_manager import preload_manager
from .window import OsInstallerWindow

APP_ID = 'com.github.p3732.OS-Installer'


class Application(Adw.Application):
    window = None

    def __init__(self, version):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)

        # Connect app shutdown signal
        self.connect('shutdown', self._on_quit)

        # Additional command line options
        self.add_main_option('demo-mode', b'd', GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Run in demo mode. Does not alter the system", None)
        self.add_main_option('test-mode', b't', GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Run in testing mode. Does not alter the system, but runs scripts.", None)

        config.set('version', version)
        global_state.send_notification = self._send_notification
        preload_manager.start()

    def _setup_quit_action(self):
        gio_action = Gio.SimpleAction.new('quit', None)
        gio_action.connect('activate', self._on_quit)
        self.add_action(gio_action)
        self.set_accels_for_action('app.quit', ['<Ctl>q'])

    def _setup_icons(self):
        icon_theme = Gtk.IconTheme.get_for_display(self.window.get_display())
        icon_theme.add_resource_path('/com/github/p3732/os-installer/')
        icon_theme.add_resource_path('/com/github/p3732/os-installer/icon')

    ### parent functions ###

    def do_activate(self):
        # create window if not existing
        if window := self.props.active_window:
            window.present()
        else:
            self.window = OsInstallerWindow(application=self)
            self._setup_icons()
            self.window.connect("close-request", self._on_quit)
            self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        options = options.end().unpack()

        if 'demo-mode' in options:
            if 'test-mode' in options:
                print("Only one of demo and test mode can be set at a time! Using demo mode.")
            global_state.demo_mode = True
        elif 'test-mode' in options:
            global_state.test_mode = True

        self.activate()
        return 0

    def do_startup(self):
        # Startup application
        self.set_resource_base_path('/com/github/p3732/os-installer')
        Adw.Application.do_startup(self)
        self._setup_quit_action()

    ### callbacks ###

    def _on_quit(self, action, param=None):
        if global_state.installation_running:
            # show confirm dialog
            self.window.show_confirm_quit_dialog(self.quit)
            # return True to avoid further processing of event
            return True
        else:
            self.quit()

    def _send_notification(self, title, text):
        n = Gio.Notification()
        n.set_title(title)
        n.set_body(text)
        self.send_notification(APP_ID, n)

def main(version):
    app = Application(version)
    return app.run(sys.argv)
