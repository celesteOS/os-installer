# SPDX-License-Identifier: GPL-3.0-or-later

from .config import config
from  pathlib import Path
from  typing import Union

class Page:
    image: Union[str, Path, None] = None
    can_reload: bool = False

    def _subscribe(self, variable, func):
        config.subscribe(variable, func)
        if hasattr(self, "subscriptions"):
            self.subscriptions.append((variable, func))
        else:
            self.subscriptions = [(variable, func)]

    ### dummy stubs ###

    def load(self):
        '''
        Called before the page is shown.
        Pages can overwrite this to receive a call every time.
        Specialld handled return values are:
        "load_prev", "pass".
        '''
        pass

    def unload(self):
        '''
        Called before the page is no longer shown. Used for e.g. storing current enrty values.
        '''
        pass

    ### public methods ###

    def cancel_subscriptions(self):
        if hasattr(self, "subscriptions"):
            for variable, func in self.subscriptions:
                config.unsubscribe(variable, func)
