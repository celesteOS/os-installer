# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum
from threading import Lock
import traceback
import yaml


class RunMode(Enum):
    default = 0
    test = 1
    demo = 2


default_config = {
    # general
    'distribution_name': 'Untitled',
    'scripts': {'prepare': None, 'install': None, 'configure': None},
    # internet
    'internet': {
        'connection_required': True,
        'checker_url': 'http://nmcheck.gnome.org/check_network_status.txt'
    },
    # language
    'fixed_language': False,
    # welcome
    'welcome_page': {'usage': True, 'logo': None, 'text': None},
    # disk
    'disk': {'partition_ok': False, 'min_size': 5},
    'disk_encryption': {'offered': True, 'forced': False, 'generated': False, 'min_length': 1, 'confirmation': False},
    # desktop
    'desktop': [],
    # user
    'user': {'min_password_length': 1, 'request_username': False, 'provide_autologin': False, 'password_confirmation': False},
    # optional pages
    'skip_region': False,
    'skip_user': False,
    # software
    'additional_software': [],
    # feature
    'additional_features': [],
    # install
    'install_slideshow': [],
    # fail
    'failure_help_url': 'https://duckduckgo.com/?q="os-installer {}"+"failed installation"',
    # commands
    'commands': {'browser': 'epiphany', 'disks': 'gnome-disks', 'reboot': 'reboot', 'wifi': 'gnome-control-center wifi'},
}

legacy_values = {
    'offer_disk_encryption': ['disk_encryption', 'offered'],
    'minimum_disk_size': ['disk', 'min_size'],
    'internet_connection_required': ['internet', 'connection_required'],
    'internet_checker_url': ['internet', 'checker_url'],
    'browser_cmd': ['commands', 'browser'],
    'disks_cmd': ['commands', 'disks'],
    'wifi_cmd': ['commands', 'wifi'],
    'skip_locale': ['skip_region'],
    'suggested_languages': None,
}

# not configurable via config file
internal_values = {
    # configurations
    'internet_connection': False,
    'use_encryption': False,
    'encryption_pin': '',
    'desktop_chosen': ('', ''),
    'user_name': '',
    'user_username': '',
    'user_autologin': False,
    'user_password': '',
    'formats': ('en_US.UTF-8', 'United States'),
    'timezone': 'UTC',
    'feature_choices': {},
    'software_choices': {},
    # other
    'installation_running': False,
    'min_disk_size_str': '',
    'send_notification': None,
    'terminal-placeholder': None,
    'display-toast': None,
    'version': -1,
}

fallback_values = {
    'available_translations': ['en_US'],
    'language_use_fixed': False,
    'language_chosen': None,
    'keyboard_language': ('en_US' 'English (US)'),
    'keyboard_layout': ('us', 'English (US)'),
    'chosen_device': None,
    'disk_is_partition': False,
    'disk_efi_partition': '/dev/null',
    'internet_page_image': 'network-wireless-disabled-symbolic',
    'welcome_page_image': 'weather-clear-symbolic',
}


def _match(variables, var, *ok_types):
    if not var in variables:
        print(f'Config error: {var} does not exist.')
        return False
    elif type(variables[var]) not in ok_types:
        print(f'Config error: {var} not of expected type (expected ',
              f'{ok_types}, but got {type(variables[var])})')
        return False
    else:
        return True


def _validate_scripts(variables):
    scripts = variables.get('scripts', None)
    if (not _match(variables, 'scripts', dict) or
            (scripts['install'] is None and scripts['configure'] is None)):
        print('Config error: Either install or configure script must exist. '
              'This setup will not be able to install anything.')
        return False
    return True


def _validate(variables):
    assert not variables['fixed_language'] == True, 'Need to specify or disable fixed language.'

    return (
        _match(variables, 'welcome_page', dict) and
        _match(variables['welcome_page'], 'usage', bool) and
        _match(variables['welcome_page'], 'logo', str, type(None)) and
        _match(variables['welcome_page'], 'text', str, type(None)) and
        _match(variables, 'internet', dict) and
        _match(variables['internet'], 'connection_required', bool) and
        _match(variables['internet'], 'checker_url', str) and
        _match(variables, 'disk', dict) and
        _match(variables['disk'], 'min_size', int, float) and
        _match(variables['disk'], 'partition_ok', bool) and
        _match(variables, 'disk_encryption', dict) and
        _match(variables['disk_encryption'], 'offered', bool) and
        _match(variables['disk_encryption'], 'forced', bool) and
        _match(variables['disk_encryption'], 'generated', bool) and
        _match(variables['disk_encryption'], 'min_length', int) and
        _match(variables['disk_encryption'], 'confirmation', bool) and
        _match(variables, 'user', dict) and
        _match(variables['user'], 'min_password_length', int) and
        _match(variables['user'], 'request_username', bool) and
        _match(variables['user'], 'provide_autologin', bool) and
        _match(variables['user'], 'password_confirmation', bool) and
        _match(variables, 'additional_software', list) and
        _match(variables, 'additional_features', list) and
        _match(variables, 'install_slideshow', list) and
        _match(variables, 'distribution_name', str) and
        _match(variables, 'fixed_language', bool, str))


class Config:
    def __init__(self):
        self.variables = default_config
        self.subscription_lock = Lock()
        self.subscriptions = {}
        self.initialized = False
        self.run_mode = RunMode.default

    def _load_from_file(self, file):
        config_from_file = yaml.load(file, Loader=yaml.Loader)
        for config_property in config_from_file:
            if config_property in legacy_values:
                self._handle_legacy(
                    config_property, config_from_file[config_property])
            elif not config_property in default_config:
                print(f'Ignoring unknown config for "{config_property}"')
            elif type(self.variables[config_property]) is dict:
                for key, value in config_from_file[config_property].items():
                    self.variables[config_property][key] = value
            else:
                self.variables[config_property] = config_from_file[config_property]

    def _handle_legacy(self, legacy_prop, legacy_val):
        replacement = legacy_values[legacy_prop]

        # moved
        if type(replacement) == list:
            # hardcoded for depth of 2, can be made variable if needed
            print(f'Developer hint: "{legacy_prop}" is deprecated, '
                  f'use "{replacement[0]} -> {replacement[1]}" instead')
            self.variables[replacement[0]][replacement[1]] = legacy_val
        # removed
        elif replacement == None:
            match legacy_prop:
                case 'suggested_languages':
                    reason = ', instead all languages with translations are listed'
                case _:
                    reason = ' without replacement'
            print(f'Developer hint: "{legacy_prop}" has been removed{reason}')
        # conditional replacement
        elif len(replacement) == 4:
            new_var, compare_val, new1, new2 = replacement
            print(f'Developer hint: "{legacy_prop}" is deprecated, '
                  f'use "{new_var}" instead')
            self.variables[new_var] = new1 if legacy_val == compare_val else new2

    def _preprocess_values(self):
        GIGABYTE_FACTOR = 1000 * 1000 * 1000
        self.variables['disk']['min_size'] *= GIGABYTE_FACTOR

    def _update_subscribers(self, variable, new_value):
        subscribers = []
        with self.subscription_lock:
            if variable in self.subscriptions:
                subscribers = self.subscriptions[variable]
        for func in subscribers:
            func(new_value)

    ### public methods ###

    def bump(self, variable):
        self._update_subscribers(variable, self.get(variable))

    def get(self, variable):
        if variable in self.variables:
            return self.variables[variable]
        elif variable in fallback_values:
            print(f'Using fallback value for {variable}')
            return fallback_values[variable]
        else:
            print(f'Requested "{variable}" not in config')
            return None

    def has(self, variable):
        return variable in self.variables

    def init(self, config_path, demo_mode, test_mode):
        if demo_mode and test_mode:
            print("Only one of demo and test mode can be set at a time! "
                  "Using demo mode.")
            self.run_mode = RunMode.demo
        elif demo_mode:
            self.run_mode = RunMode.demo
        elif test_mode:
            self.run_mode = RunMode.test

        use_default_error = None
        try:
            with open(config_path, 'r') as file:
                self._load_from_file(file)
            if not _validate(self.variables) or not _validate_scripts(self.variables):
                use_default_error = 'Config errors'
        except FileNotFoundError as e:
            use_default_error = 'Could not find config file'
        except Exception as e:
            print(f'Error loading config: {e}')
            use_default_error = 'Check if the config contains syntax errors'

        if use_default_error:
            print(f'{use_default_error}. Running in demo mode.')
            self.variables = default_config

            # Test default config to assure it doesn't contain errors
            if self.run_mode == RunMode.test and not _validate(default_config):
                print('Developer error: Default config contains errors!')
            self.run_mode = RunMode.demo

        self.variables.update(internal_values)
        self._preprocess_values()
        self.initialized = True

    def is_demo(self):
        return self.run_mode == RunMode.demo

    def is_test(self):
        return self.run_mode == RunMode.test

    def set(self, variable, new_value):
        '''Returns whether config was changed.'''
        if self.variables.get(variable, None) == new_value:
            return False

        if not self.initialized and not variable in fallback_values:
            # Non-config variables should have fallback values
            print(f'Internal error: Setting {variable} before config was read!')
            traceback.print_stack()
        self.variables[variable] = new_value

        self._update_subscribers(variable, new_value)

        return True

    def set_next_page(self, page):
        '''Convenience function'''
        self.set('displayed-page', ('next', page))
        return False

    def steal(self, variable):
        if variable in self.variables:
            return self.variables.pop(variable)

    def subscribe(self, variable, func, delayed=False):
        with self.subscription_lock:
            if variable in self.subscriptions:
                self.subscriptions[variable].append(func)
            else:
                self.subscriptions[variable] = [func]
        if delayed:
            return
        if variable in self.variables:
            func(self.variables[variable])
        elif not variable in fallback_values:
            print(f'Internal error: Subscribing to unknown {variable}')

    def unsubscribe(self, obj):
        with self.subscription_lock:
            for subs in self.subscriptions.values():
                for func in subs:
                    if hasattr(func, '__self__') and func.__self__ == obj:
                        subs.remove(func)


config = Config()
