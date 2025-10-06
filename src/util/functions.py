# SPDX-License-Identifier: GPL-3.0-or-later

import subprocess

from .config import config


def execute(args):
    if not config.is_demo() and not config.is_test():
        subprocess.run(args)


def reset_model(model, new_values):
    '''
    Reset given model to contain the passed new values.
    (Convenience wrapper)
    '''
    n_prev_items = model.get_n_items()
    model.splice(0, n_prev_items, new_values)
