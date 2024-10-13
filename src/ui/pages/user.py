# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/user.ui')
class UserPage(Gtk.Box):
    __gtype_name__ = __qualname__

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
        config.set('user_autologin', self.autologin_row.get_active())
        self._set_continue_button()

    @Gtk.Template.Callback('focus_password')
    def _focus_password(self, row):
        self.password_row.grab_focus()

    @Gtk.Template.Callback('user_name_changed')
    def _user_name_changed(self, editable):
        config.set('user_name', editable.get_text().strip())
        self._set_continue_button()

    @Gtk.Template.Callback('password_changed')
    def _password_changedentry_changed(self, editable):
        config.set('user_password', editable.get_text())
        self._set_continue_button()

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        if self.continue_button.get_sensitive():
            config.set_next_page(self)
