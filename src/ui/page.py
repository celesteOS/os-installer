# SPDX-License-Identifier: GPL-3.0-or-later

from .config import config
from  pathlib import Path
from  typing import Union

class Page:
    image: Union[str, Path, None] = None

    ### dummy stubs ###

    def load(self):
        '''
        Called before the page is shown.
        Pages can overwrite this to receive a call every time.
        Specialld handled return values are:
        "load_prev", "pass".
        '''
        pass
