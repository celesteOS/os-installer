# SPDX-License-Identifier: GPL-3.0-or-later

from .config import config


page_order = [
    'language',
    'welcome',
    # required pre-install info
    'keyboard-overview',
    'internet',
    'disk',
    'partition',
    'encrypt',
    'desktop',
    'confirm',
    # configuration
    'user',
    'locale',
    'software',
    'feature',
    # fixed block towards end
    'summary',
    'install',
    'done',
    'restart']


class StateMachine:
    def __init__(self):
        self.latest_page = 0

    def transition(self, prev_page, reached_page):
        ret_val = None

        new_index = page_order.index(reached_page)
        if self.latest_page >= new_index:
            return ret_val

        for page in page_order[self.latest_page+1:new_index+1]:
            match page:
                case 'user':
                    if prev_page == 'confirm':
                        ret_val = 'no_return'
                case 'done' | 'failed' | 'install' | 'restart' | 'summary':
                    ret_val = 'no_return'
        self.latest_page = new_index

        return ret_val


state_machine = StateMachine()
