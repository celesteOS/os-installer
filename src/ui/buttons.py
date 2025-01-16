# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk


class ContinueButton(Gtk.Button):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Translators: On button.
        self.set_label(_("_Continue"))
        self.set_use_underline(True)

        self.set_css_classes(["suggested-action", "pill"])
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.START)

        self.set_focusable(True)


class ConfirmButton(ContinueButton):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Translators: On button.
        self.set_label(_("_Confirm"))

        self.set_css_classes(["destructive-action", "pill"])
