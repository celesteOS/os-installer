# SPDX-License-Identifier: GPL-3.0-or-later

from .config import config
from  pathlib import Path
from  typing import Union

class Page:
    image: Union[str, Path, None] = None
