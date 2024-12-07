# SPDX-License-Identifier: GPL-3.0-or-later

from locale import gettext as _

from gi.repository import Gdk, GObject, Gtk

from .config import config
from .config_translation import config_translation
from .desktop_provider import desktop_provider


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/desktop_entry.ui')
class DesktopEntry(Gtk.Button):
    __gtype_name__ = __qualname__

    def __init__(self, desktop, **kwargs):
        self.desktop = desktop
        self._name = _(self.desktop.name)
        super().__init__(**kwargs)

    @GObject.Property(type=Gdk.Texture)
    def texture(self):
        return self.desktop.texture

    @GObject.Property(type=str)
    def name(self):
        return self._name


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/desktop.ui')
class DesktopPage(Gtk.Box):
    __gtype_name__ = __qualname__

    grid = Gtk.Template.Child()
    continue_button = Gtk.Template.Child()
    selected_description = Gtk.Template.Child()
    selected_image = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.button_label = self.continue_button.get_label()
        self.selected_entry = None

        number = 0
        with config_translation:
            for desktop in desktop_provider.get_desktops():
                entry = DesktopEntry(desktop)
                entry.connect('clicked', self._desktop_activated)
                if number == 0:
                    self._set_selected_desktop(entry)
                self.grid.attach(entry, number % 3, int(number/3), 1, 1)
                number += 1

    def _set_selected_desktop(self, entry):
        desktop = entry.desktop
        self.continue_button.set_label(self.button_label.format(desktop.name))
        self.selected_image.set_paintable(None)
        self.selected_image.set_paintable(desktop.texture)

        with config_translation:
            description = _(desktop.description)
        self.selected_description.set_label(description)

        if self.selected_entry:
            self.selected_entry.remove_css_class('selected-card')
            self.selected_entry.remove_css_class('suggested-action')
        entry.add_css_class('selected-card')
        entry.add_css_class('suggested-action')
        self.selected_entry = entry

        config.set('desktop_chosen', (desktop.keyword, desktop.name))

    ### callbacks ###

    def _desktop_activated(self, button):
        self._set_selected_desktop(button)
