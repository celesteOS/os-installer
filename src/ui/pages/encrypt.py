# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .config import config
from .global_state import global_state


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/encrypt.ui')
class EncryptPage(Gtk.Box):
    __gtype_name__ = __qualname__

    switch_row = Gtk.Template.Child()
    pin_row = Gtk.Template.Child()
    info_revealer = Gtk.Template.Child()

    continue_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        encryption_setting = config.get('disk_encryption')
        self.min_pin_length = max(1, encryption_setting['min_length'])
        if encryption_setting['forced']:
            self.switch_row.set_active(True)
            self.switch_row.set_visible(False)

    def _set_continue_button(self):
        needs_pin = self.switch_row.get_active()
        has_pin = len(self.pin_row.get_text()) >= self.min_pin_length
        self.continue_button.set_sensitive(not needs_pin or has_pin)

    ### callbacks ###

    @Gtk.Template.Callback('encryption_row_clicked')
    def _encryption_row_clicked(self, row, state):
        state = self.switch_row.get_active()
        config.set('use_encryption', state)
        self.pin_row.set_sensitive(state)
        self.info_revealer.set_reveal_child(state)
        self._set_continue_button()

        if state:
            self.pin_row.grab_focus()
        else:
            config.set('encryption_pin', '')

    @Gtk.Template.Callback('pin_changed')
    def _pin_changed(self, editable):
        config.set('encryption_pin', editable.get_text())
        self._set_continue_button()

    @Gtk.Template.Callback('continue')
    def _continue(self, object):
        if self.continue_button.is_sensitive():
            global_state.advance(self)
