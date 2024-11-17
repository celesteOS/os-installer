# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GnomeDesktop, GWeather

from .config import config
from .filterable_object import FilterableObject
from .preloadable import Preloadable


def _printable_timezone(id):
    return id.replace('_', ' ')


def _get_location_children(location):
    current_child = None
    children = []
    while child := location.next_child(current_child):
        children.append(child)
        current_child = child
    return children


def _add_all_locations_to_timezone(timezone_map, id, location):
    for child in _get_location_children(location):
        timezone_map[id].add(child.get_name().lower())
        _add_all_locations_to_timezone(timezone_map, id, child)


def _recurse_location(location, timezone_map):
    for child in _get_location_children(location):
        if not child.has_timezone():
            _recurse_location(child, timezone_map)
        elif (id := child.get_timezone().get_identifier()) in timezone_map:
            _add_all_locations_to_timezone(timezone_map, id, child)
        else:
            print(f'Developer hint: Unknown timezone {id} {child.get_name()}')


class TimezoneProvider(Preloadable):
    def __init__(self):
        Preloadable.__init__(self, self._get_timezones)

    def _get_timezones(self):
        current_id = GnomeDesktop.WallClock().get_timezone().get_identifier()
        config.set('timezone', _printable_timezone(current_id))

        timezone_map = dict()
        for timezone in GWeather.Location().get_world().get_timezones():
            timezone_map[timezone.get_identifier()] = set()

        for child in _get_location_children(GWeather.Location().get_world()):
            if not child.has_timezone():  # skips UTC and Etc/GMT+12
                _recurse_location(child, timezone_map)

        self.timezones = []
        for id, locations in sorted(timezone_map.items()):
            printable_name = _printable_timezone(id)

            search_string = f'{printable_name.lower()}🛑'
            search_string += '🛑'.join(list(locations))

            timezone = FilterableObject(printable_name, id, search_string)
            self.timezones.append(timezone)

    ### public methods ###

    def get_timezones(self):
        self.assert_preloaded()
        return self.timezones


timezone_provider = TimezoneProvider()
