# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import GObject
from typing import NamedTuple

from .global_state import global_state

class Option(NamedTuple):
    display : str
    keyword : str


class Choice(GObject.GObject):
    __gtype_name__ = __qualname__

    def __init__(self, name, description, icon_path, suggested=False, keyword=None, options=[]):
        super().__init__()

        self.name = name
        self.description = description
        self.icon_path = icon_path

        if options:
            self.options=options
        else:
            self.options=None
            self.keyword = keyword
            self.suggested = suggested


def handle_choice(choice):
    name = choice['name']
    description = choice['description'] if 'description' in choice else ''
    icon_path = choice['icon_path'] if 'icon_path' in choice else ''

    if 'options' in choice:
        if 'keyword' in choice or 'suggested' in choice:
            print(f"Config of {name}: 'options' can't be used with 'keyword'/'suggested'")
            return None

        options = []
        for option in choice['options']:
            if not 'option' in option:
                print(f'Option for {name} not correctly configured: {option}')
                continue
            option_name = option['name'] if 'name' in option else option['option']
            options.append(Option(option_name, option['option']))

        if len(options) == 0:
            print(f'No valid options found for {name}')
            return None
        else:
            return Choice(name, description, icon_path, options=options)
    else:
        if 'keyword' in choice:
            suggested = choice['suggested'] if 'suggested' in choice else False
            return Choice(name, description, icon_path, suggested=suggested, keyword=choice['keyword'])
        else:
            print(f'No keyword found for {name}')
            return None

def handle_legacy(choice):
    if 'package' in choice:
        print("Syntax changed! Use 'keyword' instead of 'package'")
        choice['keyword'] = choice['package']
    if 'feature' in choice:
        print("Syntax changed! Use 'keyword' instead of 'feature'")
        choice['keyword'] = choice['feature']


def handle_choices(config_entries):
    choices : list = []
    for choice in config_entries:
        handle_legacy(choice)
        if (not 'name' in choice or not
                ('options' in choice or 'keyword' in choice)):
            print(f'Choice not correctly configured: {choice}')
            continue
        if parsed := handle_choice(choice):
            choices.append(parsed)

    return choices


### public methods ###

@staticmethod
def get_software_suggestions():
    if software := global_state.get_config('additional_software'):
        return handle_choices(software)
    else:
        return []

@staticmethod
def get_feature_suggestions():
    if features := global_state.get_config('additional_features'):
        return handle_choices(features)
    else:
        return []
