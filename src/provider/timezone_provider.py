# SPDX-License-Identifier: GPL-3.0-or-later

from time import time

from gi.repository import GnomeDesktop, GObject, GWeather

from .config import config
from .preloadable import Preloadable


def printable_timezone(id):
    return id.replace('_', ' ')


class Timezone(GObject.Object):
    __gtype_name__ = __qualname__

    def __init__(self, id):
        super().__init__()

        self.id: str = id
        self.name: str = printable_timezone(id)
        self.locations: set = set()
        self.search_string = ''

    @GObject.Property(type=str)
    def title(self):
        return self.name


def _get_location_children(location):
    current_child = None
    children = []
    while child := location.next_child(current_child):
        children.append(child)
        current_child = child
    return children


def _add_all_locations_to_timezone(timezone, location):
    for child in _get_location_children(location):
        timezone.locations.add(child.get_name().lower())
        _add_all_locations_to_timezone(timezone, child)


def _recurse_location(location, timezone_map):
    for child in _get_location_children(location):
        if not child.has_timezone():
            _recurse_location(child, timezone_map)
        elif (id := child.get_timezone().get_identifier()) in timezone_map:
            _add_all_locations_to_timezone(timezone_map[id], child)
        else:
            print(f'Developer hint: Unknown timezone {id} {child.get_name()}')


class TimezoneProvider(Preloadable):
    def __init__(self):
        Preloadable.__init__(self, self._get_timezones)

    def _get_timezones(self):
        current_id = GnomeDesktop.WallClock().get_timezone().get_identifier()
        config.set('timezone', printable_timezone(current_id))

        timezone_map = dict()
        for timezone in GWeather.Location().get_world().get_timezones():
            id = timezone.get_identifier()
            timezone_map[id] = Timezone(id)

        for child in _get_location_children(GWeather.Location().get_world()):
            if not child.has_timezone():  # skips UTC and Etc/GMT+12
                _recurse_location(child, timezone_map)

        self.timezones = []
        for timezone in sorted(timezone_map.values(), key=lambda t: t.name):
            locations_list = list(timezone.locations)
            timezone.search_string = f'{timezone.name.lower()}🛑'
            timezone.search_string += '🛑'.join(locations_list)
            timezone.locations = None
            self.timezones.append(timezone)

    ### public methods ###

    def get_timezones(self):
        self.assert_preloaded()
        return self.timezones


timezone_provider = TimezoneProvider()
