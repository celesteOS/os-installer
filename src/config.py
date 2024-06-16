# SPDX-License-Identifier: GPL-3.0-or-later

import yaml

DEFAULT_CONFIG_PATH = '/etc/os-installer/config.yaml'


default_config = {
    # general
    'distribution_name': 'Untitled',
    'demo_mode': False,
    'test_mode': False,
    # internet
    'internet_connection_required': True,
    'internet_checker_url': 'http://nmcheck.gnome.org/check_network_status.txt',
    # language
    'suggested_languages': ['en', 'ar', 'de', 'es', 'fr', 'ja', 'ru', 'zh'],
    'fixed_language': False,
    # welcome
    'welcome_page': {'usage': True, 'logo': None, 'text': None},
    # disk
    'minimum_disk_size': 5,
    'offer_disk_encryption': True,
    # optional pages
    'skip_user': False,
    'skip_locale': False,
    # software
    'additional_software': [],
    # feature
    'additional_features': [],
    # fail
    'failure_help_url': 'https://duckduckgo.com/?q="os-installer {}"+"failed installation"',
    # commands
    'browser_cmd': 'epiphany',
    'disks_cmd': 'gnome-disks',
    'wifi_cmd': 'gnome-control-center wifi',

    # not configurable
    'version': -1,
}

optional_defaults = {
    'use_encryption': False,
    'encryption_pin': '',
    'user_name': '',
    'user_autologin': False,
    'user_password': '',
    'formats_locale': 'en_US.UTF-8',
    'formats_ui': 'United States',
    'timezone': 'UTC',
    'chosen_software_packages': '',
    'chosen_software': [],
    'chosen_feature_names': '',
    'chosen_features': []
}

fallback_values = {
    'language': ('en_US', 'English for Dummies'),
    'locale': 'en_US.UTF-8',
    'keyboard_language': ('en_US' 'English (US)'),
    'keyboard_layout': ('us', 'English (US)'),
    'disk_device_path': '/dev/null',
    'disk_is_partition': False,
    'disk_efi_partition': '/dev/null',
    'disk_name': 'Test Dummy'
}


def _match(variables, var, *ok_types):
    if not var in variables:
        print(f'Config error: {var} does not exist.')
        return False
    elif type(variables[var]) not in ok_types:
        print(f'Config error: {var} not of expected type (expected ',
              f'{ok_types}, but got {has_type})')
        return False
    else:
        return True


def _validate(variables):
    assert not variables['fixed_language'] == True, 'Need to specify or disable fixed language.'

    return (
        _match(variables, 'welcome_page', dict) and
        _match(variables['welcome_page'], 'usage', bool) and
        _match(variables['welcome_page'], 'logo', str, type(None)) and
        _match(variables['welcome_page'], 'text', str, type(None)) and
        _match(variables, 'internet_connection_required', bool) and
        _match(variables, 'internet_checker_url', str) and
        _match(variables, 'suggested_languages', list) and
        _match(variables, 'minimum_disk_size', int) and
        _match(variables, 'offer_disk_encryption', bool) and
        _match(variables, 'additional_software', list) and
        _match(variables, 'additional_features', list) and
        _match(variables, 'distribution_name', str) and
        _match(variables, 'fixed_language', bool, str))


class Config:
    def __init__(self):
        self.variables = default_config
        self.subscriptions = {}

        try:
            with open(DEFAULT_CONFIG_PATH, 'r') as file:
                self._load_from_file(file)
        except Exception as e:
            print(f'Error loading config: {e}. Check if the config contains '
                  'syntax errors.')
            self.variables = default_config
        if not _validate(self.variables):
            print('Config errors, loading default config.')
            self.variables = default_config
        self.variables.update(optional_defaults)
        self._preprocess_values()

    def _load_from_file(self, file):
        config_from_file = yaml.load(file, Loader=yaml.Loader)
        for config_property in config_from_file:
            if type(self.variables[config_property]) is dict:
                for key, value in config_from_file[config_property].items():
                    self.variables[config_property][key] = value
            else:
                self.variables[config_property] = config_from_file[config_property]

    def _preprocess_values(self):
        GIGABYTE_FACTOR = 1000 * 1000 * 1000
        self.variables['minimum_disk_size'] *= GIGABYTE_FACTOR

    ### public methods ###

    def get(self, variable):
        if variable in self.variables:
            return self.variables[variable]
        # TODO when global_state independent of config:
        # elif global_state.test_mode and variable in fallback_values:
        #     return fallback_values[variable]
        else:
            print(f'Requested {variable} not in config')
            return None

    def has(self, variable):
        return variable in self.variables

    def set(self, variable, value):
        self.variables[variable] = value

        if variable in self.subscriptions:
            for func in self.subscriptions[variable]:
                func(value)

    def subscribe(self, variable, func):
        if variable in self.subscriptions:
            self.subscriptions[variable].append(func)
        else:
            self.subscriptions[variable] = [func]
        func(self.variables[variable])

    def unsubscribe(self, variable, func):
        if variable in self.subscriptions and func in self.subscriptions[variable]:
            self.subscriptions[variable].remove(func)
        else:
            print(f'Unsubscribing non-subscribed function {func}!')


config = Config()
