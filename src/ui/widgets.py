# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from gi.repository import Adw, Gtk


def reset_model(model, new_values):
    '''
    Reset given model to contain the passed new values.
    (Convenience wrapper)
    '''
    n_prev_items = model.get_n_items()
    model.splice(0, n_prev_items, new_values)

@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/device_row.ui')
class DeviceRow(Adw.ActionRow):
    __gtype_name__ = __qualname__

    stack = Gtk.Template.Child()
    size_label = Gtk.Template.Child()
    too_small_label = Gtk.Template.Child()

    def __init__(self, info, required_size_str=None, **kwargs):
        super().__init__(**kwargs)

        self.info = info
        self.size_label.set_label(info.size_text)
        if info.name:
            self.set_title(info.name)

        self.set_subtitle(info.device_path)

        if required_size_str:
            smol = self.too_small_label.get_label()
            self.too_small_label.set_label(smol.format(required_size_str))
            self.set_activatable(False)
            self.set_sensitive(False)
            self.stack.set_visible_child_name('too_small')


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/labeled_image.ui')
class LabeledImage(Gtk.Box):
    __gtype_name__ = __qualname__

    image = Gtk.Template.Child()
    title = Gtk.Template.Child()

    def __init__(self, image_source, label, **kwargs):
        super().__init__(**kwargs)

        if isinstance(image_source, str):
            self.image.set_from_icon_name(image_source)
        elif isinstance(image_source, Path):
            self.image.set_from_file(str(image_source))
        else:
            print('Developer hint: invalid title image')
            # ignoring

        self.title.set_label(label)


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/multi_selection_row.ui')
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


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/progress_row.ui')
class ProgressRow(Gtk.ListBoxRow):
    __gtype_name__ = __qualname__

    title = Gtk.Template.Child()

    def __init__(self, label, additional_info = None, **kwargs):
        super().__init__(**kwargs)

        self.title.set_label(label)

        self.info = additional_info

    def get_label(self):
        return self.title.get_label()


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/selection_row.ui')
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


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/summary_row.ui')
class SummaryRow(Gtk.ListBoxRow):
    __gtype_name__ = __qualname__

    icon = Gtk.Template.Child()
    name = Gtk.Template.Child()

    def __init__(self, choice, **kwargs):
        super().__init__(**kwargs)

        if choice.options:
            self.name.set_label(choice.state.display)
        else:
            self.name.set_label(choice.name)

        if choice.icon_path:
            self.icon.set_from_file(choice.icon_path)
        else:
            self.icon.set_from_icon_name(choice.icon_name)
