# SPDX-License-Identifier: GPL-3.0-or-later

import re

from gi.repository import Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/user.ui')
class UserPage(Gtk.Box):
    __gtype_name__ = __qualname__

    name_row = Gtk.Template.Child()
    username_row = Gtk.Template.Child()
    autologin_row = Gtk.Template.Child()
    password_row = Gtk.Template.Child()
    password_error_indicator = Gtk.Template.Child()
    continue_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        user_setting = config.get('user')
        self.min_password_length = user_setting['min_password_length']
        self.request_username = user_setting['request_username']

        self.name_ok = False
        self.username_ok = False
        self.username_error = None
        self.password_ok = self.min_password_length <= 0
        self.password_error = None

        self.name_row.set_text(config.get('user_name'))
        self.username_row.set_visible(self.request_username)
        if self.request_username:
            self.username_row.set_text(config.get('user_username'))
        else:
            self.username_ok = True
        if user_setting['provide_autologin']:
            self.autologin_row.set_visible(True)
            self.autologin_row.set_active(config.get('user_autologin'))
        else:
            self.autologin_row.set_visible(False)
            self.autologin_row.set_active(False)
        self.password_row.set_text(config.get('user_password'))

    def _set_continue_button(self):
        self.continue_button.set_sensitive(self.name_ok and self.username_ok and self.password_ok)

    ### callbacks ###

    @Gtk.Template.Callback('autologin_row_clicked')
    def _autologin_row_clicked(self, row, state):
        config.set('user_autologin', self.autologin_row.get_active())
        self._set_continue_button()

    @Gtk.Template.Callback('focus_password')
    def _focus_password(self, row):
        self.password_row.grab_focus()

    @Gtk.Template.Callback('focus_next_from_name')
    def _focus_next_from_name(self, row):
        if self.request_username:
            self.username_row.grab_focus()
        else:
            self.password_row.grab_focus()

    @Gtk.Template.Callback('name_changed')
    def _name_changed(self, editable):
        name = editable.get_text().strip()
        config.set('user_name', name)
        self.name_ok = len(name) > 0
        self._set_continue_button()

    @Gtk.Template.Callback('username_changed')
    def _username_changed(self, editable):
        username = editable.get_text().strip()
        self.username_ok = bool(re.match('^[a-z][a-z0-9_-]*$', username))
        if self.username_ok:
            config.set('user_username', username)
            if self.username_error:
                self.username_row.remove_css_class('error')
                self.username_row.remove(self.username_error)
                self.username_error = None
        elif len(username) > 0 and not self.username_error:
            self.username_row.add_css_class('error')
            self.username_error = Gtk.Image.new_from_icon_name('dialog-warning-symbolic')
            self.username_row.add_suffix(self.username_error)
        self._set_continue_button()

    @Gtk.Template.Callback('password_changed')
    def _password_changedentry_changed(self, editable):
        password = editable.get_text()
        self.password_ok = len(password) >= self.min_password_length
        if self.password_ok:
            config.set('user_password', password)
            if self.password_error:
                self.password_row.remove_css_class('error')
                self.password_row.remove(self.password_error)
                self.password_error = None
        elif len(password) > 0 and not self.password_error:
            self.password_row.add_css_class('error')
            self.password_error = Gtk.Image.new_from_icon_name('dialog-warning-symbolic')
            self.password_row.add_suffix(self.password_error)
        self._set_continue_button()

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        if self.continue_button.get_sensitive():
            config.set_next_page(self)
