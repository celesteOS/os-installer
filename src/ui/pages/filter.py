# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum
from gi.repository import Gtk

from .format_provider import get_formats
from .global_state import global_state
from .page import Page
from .system_calls import set_system_formats, set_system_timezone
from .timezone_provider import get_timezones
from .widgets import reset_model, ProgressRow


class FilterType(Enum):
    format = 0
    timezone = 1


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/filter.ui')
class FilterPage(Gtk.Box, Page):
    __gtype_name__ = __qualname__
    image = 'map-symbolic'

    format_title = Gtk.Template.Child()
    timezone_title = Gtk.Template.Child()

    search_entry = Gtk.Template.Child()
    custom_filter = Gtk.Template.Child()
    filter_list_model = Gtk.Template.Child()

    stack = Gtk.Template.Child()
    list = Gtk.Template.Child()
    list_loaded = False
    list_model = Gtk.Template.Child()

    def __init__(self, filter_type, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        self.type = filter_type
        match self.type:
            case FilterType.format:
                self.format_title.set_visible(True)
                self.filter = self._format_filter
            case FilterType.timezone:
                self.timezone_title.set_visible(True)
                self.filter = self._timezone_filter

        self.search_entry.connect("search-changed", self._filter)

        self.list.bind_model(
            self.filter_list_model, lambda f: ProgressRow(f.name))

    def _filter(self, *args):
        self.search_text = self.search_entry.get_text().lower()
        self.custom_filter.set_filter_func(self.filter)

        if self.filter_list_model.get_n_items() > 0:
            self.stack.set_visible_child_name('list')
        else:
            self.stack.set_visible_child_name('none')

    def _format_filter(self, format):
        return self.search_text in format.lower_case_name or format.locale.startswith(self.search_text)

    def _timezone_filter(self, timezone):
        if self.search_text in timezone.lower_case_name:
            return True
        for location in timezone.locations:
            if self.search_text in location:
                return True
        return False

    ### callbacks ###

    @Gtk.Template.Callback('row_selected')
    def _row_selected(self, list_box, row):
        match self.type:
            case FilterType.format:
                set_system_formats(row.info, row.get_label())
            case FilterType.timezone:
                set_system_timezone(row.get_label())
        global_state.advance(self)

    ### public methods ###

    def load(self):
        if not self.list_loaded:
            self.list_loaded = True
            match self.type:
                case FilterType.format:
                    model = get_formats()
                case FilterType.timezone:
                    model = get_timezones()
            reset_model(self.list_model, model)


FormatPage = lambda **args: FilterPage(FilterType.format, **args)
TimezonePage = lambda **args: FilterPage(FilterType.timezone, **args)
