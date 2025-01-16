# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw


class ConfirmQuitDialog(Adw.AlertDialog):
    __gtype_name__ = __qualname__

    def __init__(self, quit_func, **kwargs):
        super().__init__(**kwargs)

        self.quit_func = quit_func

        # Translators: Dialog title
        self.set_heading(_("Installation Running"))
        # Translators: Text in dialog shown if user wants to close app with installation running
        self.set_body(
            _("Stopping a running installation will leave the disk in an undefined state that might potentially be harmful"))

        # Translators: Underscore can not be the same as for 'Stop Installation'.
        self.add_response('close', _("_Continue Installation"))
        # Translators: Underscore can not be the same as for 'Continue Installation'.
        self.add_response('stop', _("_Stop Installation"))

        self.set_response_appearance('stop', Adw.ResponseAppearance.DESTRUCTIVE)
        self.set_default_response('close')
        self.set_close_response('close')

        self.connect('response', self._check_quit)

    def _check_quit(self, dialog, response):
        if response == 'stop':
            self.quit_func()
