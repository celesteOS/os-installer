# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config
from .global_state import global_state
from .page import Page


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/user.ui')
class UserPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'user-symbolic'

    user_name_row = Gtk.Template.Child()
    autologin_row = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    continue_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.user_name_row.set_text(config.get('user_name'))
        self.password_row.set_text(config.get('user_password'))
        self.autologin_row.set_active(config.get('user_autologin'))

    def _set_continue_button(self):
        has_user_name = not self.user_name_row.get_text().strip() == ''
        autologin = self.autologin_row.get_active()
        has_password = not self.password_row.get_text() == ''
        can_continue = has_user_name and (autologin or has_password)
        self.continue_button.set_sensitive(can_continue)

    ### callbacks ###

    @Gtk.Template.Callback('autologin_row_clicked')
    def _autologin_row_clicked(self, row, state):
        self._set_continue_button()

    @Gtk.Template.Callback('focus_password')
    def _focus_password(self, row):
        self.password_row.grab_focus()

    @Gtk.Template.Callback('entry_changed')
    def _entry_changed(self, editable):
        self._set_continue_button()

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        if self.continue_button.get_sensitive():
            global_state.advance(self)

    ### public methods ###

    def unload(self):
        config.set('user_name', self.user_name_row.get_text().strip())
        config.set('user_password', self.password_row.get_text())
        config.set('user_autologin', self.autologin_row.get_active())
