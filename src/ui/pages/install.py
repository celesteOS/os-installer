# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .installation_scripting import installation_scripting


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/install.ui')
class InstallPage(Gtk.Box):
    __gtype_name__ = __qualname__

    terminal_box = Gtk.Template.Child()
    stack = Gtk.Template.Child()
    spinner = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        # UI element states
        self.terminal_box.append(installation_scripting.terminal)
        self.stack.set_visible_child_name('spinner')
        self.spinner.start()
        config.subscribe('installation_running', self._installation_done)

    def _installation_done(self, _):
        self.terminal_box.remove(installation_scripting.terminal)
        self.spinner.stop()

    ### callbacks ###

    @Gtk.Template.Callback('terminal_button_toggled')
    def _terminal_button_toggled(self, toggle_button):
        if self.stack.get_visible_child_name() == 'spinner':
            self.spinner.stop()
            self.stack.set_visible_child_name('terminal')
        else:
            self.spinner.start()
            self.stack.set_visible_child_name('spinner')
