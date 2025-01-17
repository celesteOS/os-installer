# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk


def translate_widgets(*widgets):
    for widget in widgets:
        match type(widget):
            case Adw.ActionRow | Adw.EntryRow | Adw.ExpanderRow | Adw.PasswordEntryRow | Adw.SwitchRow:
                widget.set_title(_(widget.get_title()))
            case Adw.StatusPage:
                widget.set_title(_(widget.get_title()))
                widget.set_description(_(widget.get_description()))
            case Gtk.Button | Gtk.Label:
                widget.set_label(_(widget.get_label()))
            case Gtk.SearchEntry:
                widget.set_placeholder_text(_(widget.get_placeholder_text()))
            case _:
                print(f'internal: Translation unknown for type {type(widget)} ({widget})')
