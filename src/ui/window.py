# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gio, Gtk

from .config import config
from .confirm_quit_dialog import ConfirmQuitDialog
from .navigation import Navigation
from .terminal_dialog import TerminalDialog


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/main_window.ui')
class OsInstallerWindow(Adw.ApplicationWindow):
    __gtype_name__ = __qualname__

    navigation: Navigation = Gtk.Template.Child()
    terminal_holder = Gtk.Template.Child()
    toaster = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._setup_actions()
        self.connect('close-request', self._show_confirm_dialog, None)

        config.subscribe('stashed-terminal', self._stash_terminal, delayed=True)
        config.subscribe('display-toast', self._show_toast, delayed=True)

    def _stash_terminal(self, terminal):
        # VteTerminal widget needs to exist somewhere in the widget tree once
        # created. Keep it around as a stack page that never gets revealed.
        terminal = config.steal('stashed-terminal')
        self.terminal_holder.set_child(terminal)

    def _add_action(self, action_name, callback, keybinding=None):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.action_group.add_action(action)

        trigger = None
        if keybinding:
            trigger = Gtk.ShortcutTrigger.parse_string(keybinding)
        named_action = Gtk.NamedAction.new(f'win.{action_name}')
        shortcut = Gtk.Shortcut.new(trigger, named_action)
        self.shortcut_controller.add_shortcut(shortcut)

    def _setup_actions(self):
        self.action_group = Gio.SimpleActionGroup()
        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope(1))

        self._add_action('next-page', lambda _, __: self.navigation.go_forward())
        self._add_action('previous-page', lambda _, __: self.navigation.go_backward())
        self._add_action('advance', lambda page, __: self.navigation.advance(page))
        self._add_action('reload-page', lambda _, __: self.navigation.reload_page(), 'F5')

        self._add_action('about-page', self._show_about_page, '<Alt>Return')
        self._add_action('show-terminal', self._show_terminal, '<Ctl>t')
        self._add_action('quit', self._show_confirm_dialog, '<Ctl>q')

        if config.get('test_mode'):
            self._add_action('fail-page', lambda _, __: self.navigation.show_failed(), '<Alt>F')
            self._add_action('skip', lambda _, __: self.navigation.advance(), '<Alt>S')

        self.insert_action_group('win', self.action_group)
        self.add_controller(self.shortcut_controller)

    ### callbacks ###

    def _show_toast(self, toast_text):
        if toast_text := config.steal('display-toast'):
            toast = Adw.Toast.new(toast_text)
            self.toaster.add_toast(toast)

    def _show_about_page(self, _, __):
        builder = Gtk.Builder.new_from_resource('/com/github/p3732/os-installer/ui/about_dialog.ui')
        popup = builder.get_object('about_window')
        popup.present(self)

    def _show_confirm_dialog(self, _, __):
        if not config.get('installation_running'):
            self.get_application().quit()
            return False
        else:
            ConfirmQuitDialog(self.get_application().quit).present(self)
            return True

    def _show_terminal(self, _, __):
        terminal = self.terminal_holder.get_child()
        self.terminal_holder.set_child(None)
        TerminalDialog(terminal).present(self)
