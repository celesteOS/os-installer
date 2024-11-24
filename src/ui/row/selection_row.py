# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/multi_selection_row.ui')
class MultiSelectionRow(Adw.ComboRow):
    __gtype_name__ = __qualname__

    icon = Gtk.Template.Child()
    list = Gtk.Template.Child()

    def __init__(self, choice, **kwargs):
        super().__init__(**kwargs)

        self.choice = choice

        self.set_title(choice.name)
        self.set_subtitle(choice.description)
        if choice.icon_path:
            self.icon.set_from_file(choice.icon_path)
        else:
            self.icon.set_from_icon_name(choice.icon_name)
            self.icon.set_icon_size(Gtk.IconSize.LARGE)

        self.list.splice(0, 0, [option.display for option in choice.options])
        self.set_model(self.list)
        self.update_choice()

    def get_chosen_option(self):
        return self.choice.options[self.get_selected()]

    def update_choice(self):
        display_text = self.get_selected_item().get_string()
        for index, option in enumerate(self.choice.options):
            if option.display == display_text:
                self.set_selected(index)
                self.choice.state = option
                return


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/row/selection_row.ui')
class SelectionRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    icon = Gtk.Template.Child()
    switch = Gtk.Template.Child()

    def __init__(self, choice, **kwargs):
        super().__init__(**kwargs)

        self.choice = choice

        self.set_title(choice.name)
        self.set_subtitle(choice.description)
        self.switch.set_active(choice.state)
        if choice.icon_path:
            self.icon.set_from_file(choice.icon_path)
        else:
            self.icon.set_from_icon_name(choice.icon_name)
            self.icon.set_icon_size(Gtk.IconSize.LARGE)

    def is_activated(self):
        return self.switch.get_active()

    def flip_switch(self):
        new_state = not self.switch.get_active()
        self.switch.set_active(new_state)
        self.choice.state = new_state
