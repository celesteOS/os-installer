# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk


def translate_widgets(*widgets):
    for widget in widgets:
        # Covers subclassed widgets such as SummaryRow but also
        # Adw.ActionRow | Adw.EntryRow | Adw.PasswordEntryRow | Adw.SwitchRow
        if issubclass(type(widget), Adw.PreferencesRow):
            widget.set_title(_(widget.get_title()))
            continue
        match type(widget):
            case Adw.ExpanderRow:
                widget.set_title(_(widget.get_title()))
            case Adw.ButtonContent:
                widget.set_label(_(widget.get_label()))
            case Adw.StatusPage:
                widget.set_title(_(widget.get_title()))
                widget.set_description(_(widget.get_description()))
            case Gtk.Button | Gtk.Label:
                widget.set_label(_(widget.get_label()))
            case Gtk.SearchEntry:
                widget.set_placeholder_text(_(widget.get_placeholder_text()))
            case _:
                print(f'internal: Translation unknown for type {type(widget)} ({widget})')
