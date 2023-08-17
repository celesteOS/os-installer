# SPDX-License-Identifier: GPL-3.0-or-later

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
    __gtype_name__ = 'DeviceRow'

    stack = Gtk.Template.Child()
    size = Gtk.Template.Child()

    def __init__(self, info, too_small=False, **kwargs):
        super().__init__(**kwargs)

        self.info = info
        self.size.set_label(info.size_text)
        if info.name:
            self.set_title(info.name)

        self.set_subtitle(info.device_path)

        if too_small:
            self.set_activatable(False)
            self.set_sensitive(False)
            self.stack.set_visible_child_name('too_small')


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/multi_selection_row.ui')
class MultiSelectionRow(Adw.ComboRow):
    __gtype_name__ = 'MultiSelectionRow'

    icon = Gtk.Template.Child()
    list = Gtk.StringList()

    def __init__(self, title, description, icon_path, fallback_icon,
                 options, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(description)
        if not icon_path:
            self.icon.set_from_icon_name(fallback_icon)
            self.icon.set_icon_size(Gtk.IconSize.LARGE)
        else:
            self.icon.set_from_file(icon_path)

        self.icon_path = icon_path
        self.options = options

        self.list.splice(0, 0, [option.display for option in options])
        self.set_model(self.list)

    def get_chosen_option(self):
        return self.options[self.get_selected()]


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/page_wrapper.ui')
class PageWrapper(Gtk.Box):
    __gtype_name__ = 'PageWrapper'

    content = Gtk.Template.Child()

    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)

        self.content.set_child(page)

    def get_page(self):
        return self.content.get_child()

@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/progress_row.ui')
class ProgressRow(Gtk.ListBoxRow):
    __gtype_name__ = 'ProgressRow'

    title = Gtk.Template.Child()

    def __init__(self, label, additional_info = None, **kwargs):
        super().__init__(**kwargs)

        self.title.set_label(label)

        self.info = additional_info

    def get_label(self):
        return self.title.get_label()


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/selection_row.ui')
class SelectionRow(Adw.ActionRow):
    __gtype_name__ = 'SelectionRow'

    icon = Gtk.Template.Child()
    switch = Gtk.Template.Child()

    def __init__(self, title, description, icon_path, fallback_icon,
                 default_state, info, **kwargs):
        super().__init__(**kwargs)
        self.set_title(title)
        self.set_subtitle(description)
        self.switch.set_active(default_state)
        if not icon_path:
            self.icon.set_from_icon_name(fallback_icon)
            self.icon.set_icon_size(Gtk.IconSize.LARGE)
        else:
            self.icon.set_from_file(icon_path)

        self.icon_path = icon_path
        self.info = info

    def is_activated(self):
        return self.switch.get_active()

    def flip_switch(self):
        return self.switch.set_active(not self.switch.get_active())


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/summary_row.ui')
class SummaryRow(Gtk.ListBoxRow):
    __gtype_name__ = 'SummaryRow'

    icon = Gtk.Template.Child()
    name = Gtk.Template.Child()

    def __init__(self, name, icon_path, icon_name, **kwargs):
        super().__init__(**kwargs)
        self.name.set_label(name)
        if not icon_path:
            self.icon.set_from_icon_name(icon_name)
        else:
            self.icon.set_from_file(icon_path)
