# SPDX-License-Identifier: GPL-3.0-or-later

from  pathlib import Path
from  typing import Union

class Page:
    image: Union[str, Path, None] = None
    can_reload: bool = False

    loaded: bool = False

    def id(self):
        return self.__gtype_name__

    ### dummy stubs ###

    def load(self):
        '''
        Called before the page is shown.
        Pages can overwrite this to receive call every time.
        Returning True means the page can be skipped.
        '''
        if not self.loaded:
            self.loaded = True
            return self.load_once()

    def load_once(self):
        '''
        Called once on first page construction. Used for e.g. filling lists.
        Special return values: "load_next" (skips page), "prevent_back_navigation"
        '''
        return

    def unload(self):
        '''
        Called before the page is no longer shown. Used for e.g. storing current enrty values.
        '''
        return
