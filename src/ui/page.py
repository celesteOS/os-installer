# SPDX-License-Identifier: GPL-3.0-or-later

from  pathlib import Path
from  typing import Union

class Page:
    image: Union[str, Path, None] = None
    can_reload: bool = False

    def id(self):
        return self.__gtype_name__

    ### dummy stubs ###

    def load(self):
        '''
        Called before the page is shown.
        Pages can overwrite this to receive a call every time.
        Specialld handled return values are:
        "load_next", "load_prev", "prevent_back_navigation".
        '''
        pass

    def unload(self):
        '''
        Called before the page is no longer shown. Used for e.g. storing current enrty values.
        '''
        pass
