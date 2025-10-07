# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Gtk

from .buttons import ConfirmButton
from .config import config
from .device_rows import DeviceSummaryRow
from .translator import config_gettext
from .translations import translate_widgets


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/summary.ui')
class SummaryPage(Gtk.Box):
    __gtype_name__ = __qualname__

    list = Gtk.Template.Child()

    disk_row_index = 2

    # rows
    language_row = Gtk.Template.Child()
    keyboard_row = Gtk.Template.Child()
    desktop_row = Gtk.Template.Child()
    user_row = Gtk.Template.Child()
    format_row = Gtk.Template.Child()
    timezone_row = Gtk.Template.Child()
    software_row = Gtk.Template.Child()
    feature_row = Gtk.Template.Child()

    # user row specific
    user_autologin = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        translate_widgets(self.language_row, self.keyboard_row, self.desktop_row, self.user_row,
                          self.user_autologin, self.format_row, self.timezone_row, self.software_row,
                          self.feature_row)

        if config.get('desktop'):
            self.desktop_row.set_visible(True)
            config.subscribe('desktop_chosen', self._update_desktop)
        if not config.get('fixed_language'):
            self.language_row.set_visible(True)
            config.subscribe('language_chosen', self._update_language)
        if config.get('additional_features'):
            self.feature_row.set_visible(True)
            config.subscribe('feature_choices', self._update_feature_choices)
        if config.get('additional_software'):
            self.software_row.set_visible(True)
            config.subscribe('software_choices', self._update_software_choices)
        if not config.get('skip_user'):
            self.user_row.set_visible(True)
            config.subscribe('user_autologin', self._update_user_autologin)
            config.subscribe('user_name', self._update_user_name)
        if not config.get('skip_region'):
            self.format_row.set_visible(True)
            config.subscribe('formats', self._update_formats)
            self.timezone_row.set_visible(True)
            config.subscribe('timezone', self._update_timezone)

        self.has_install = config.get('scripts')['install'] is not None
        if self.has_install:
            # These values can only be edited if install step has not already
            # been started wtih them
            self.language_row.set_activatable(False)
            self.desktop_row.set_activatable(False)

        config.subscribe('keyboard_layout', self._update_keyboard_layout)
        config.subscribe('chosen_device', self._update_device_row)

    def _update_choices(self, row, choices):
        if not choices:
            # Translators: Shown when list of selected software is empty.
            row.set_subtitle(_("None"))
            return

        _ = config_gettext
        choice_texts = []
        for choice in choices:
            if choice.options:
                text = f'{_(choice.name)} – {_(choice.state.display)}'
                choice_texts.append(text)
            elif choice.state:
                choice_texts.append(_(choice.name))

        row.set_subtitle(', '.join(choice_texts))

    ### callbacks ###

    def _update_desktop(self, desktop):
        _, name = desktop
        self.desktop_row.set_subtitle(name)

    def _update_device_row(self, device):
        if device == None:
            print('Internal error: Disk was not set before summary page')
        else:
            row = self.list.get_row_at_index(self.disk_row_index)
            if type(row) == DeviceSummaryRow:
                self.list.remove(row)
            row = DeviceSummaryRow(device, not self.has_install)
            self.list.insert(row, self.disk_row_index)

    def _update_feature_choices(self, choices):
        self._update_choices(self.feature_row, choices)

    def _update_formats(self, formats):
        self.format_row.set_subtitle(formats[1])

    def _update_keyboard_layout(self, keyboard_layout):
        _, name = keyboard_layout
        self.keyboard_row.set_subtitle(name)

    def _update_language(self, language):
        self.language_row.set_subtitle(language.name)

    def _update_software_choices(self, choices):
        self._update_choices(self.software_row, choices)

    def _update_timezone(self, timezone):
        self.timezone_row.set_subtitle(timezone)

    def _update_user_autologin(self, autologin):
        self.user_autologin.set_visible(autologin)

    def _update_user_name(self, user_name):
        self.user_row.set_subtitle(user_name)

    @Gtk.Template.Callback('summary_row_activated')
    def _summary_row_activated(self, list_box, row):
        config.set('displayed-page', row.get_name())
