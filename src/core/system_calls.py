# SPDX-License-Identifier: GPL-3.0-or-later

''' All calls to other programs are encapsulated here. '''

import locale as Locale
import os
from subprocess import Popen
import subprocess

from gi.repository import Gio

from .config import config


def _exec(args):
    if not config.get('demo_mode') and not config.get('test_mode'):
        subprocess.run(args)


def _run_program(args):
    env = os.environ.copy()
    env["LANG"] = config.get('locale')
    Popen(args, env=env)


class SystemCaller:
    def __init__(self, app_window):
        self.action_group = Gio.SimpleActionGroup()

        self._add_syscall_action('error-search', self._open_internet_search)
        self._add_syscall_action('manage-disks', self._open_disks)
        self._add_syscall_action('wifi-settings', self._open_wifi_settings)

        app_window.insert_action_group('external', self.action_group)

    def _add_syscall_action(self, action_name, callback):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.action_group.add_action(action)

    def _open_disks(self, _, __):
        _run_program(config.get('commands')['disks'].split())

    def _open_internet_search(self, _, __):
        browser_cmd = config.get('commands')['browser'].split()
        failure_help_url = config.get('failure_help_url')
        version = config.get('version')
        browser_cmd.append(failure_help_url.format(version))
        _run_program(browser_cmd)

    def _open_wifi_settings(self, _, __):
        _run_program(config.get('commands')['wifi'].split())


### public methods ###

def reboot_system():
    _exec(config.get('commands')['reboot'].split())


def set_system_keyboard_layout(keyboard_info):
    config.set('keyboard_layout', (keyboard_info.layout, keyboard_info.name))
    # set system input
    _exec(['gsettings', 'set', 'org.gnome.desktop.input-sources', 'sources',
           f"[('xkb','{keyboard_info.layout}')]"])


def set_system_language(language_info):
    locale = Locale.normalize(language_info.locale)
    config.set('locale', locale)

    # set app language
    was_set = Locale.setlocale(Locale.LC_ALL, locale)
    if not was_set:
        print(f'Could not set locale to {language_info.name}, '
              'falling back to English.')
        print('Installation medium creators, check that you have correctly set up the locales',
              f'to support {language_info.name}.')
        # fallback
        Locale.setlocale(Locale.LC_ALL, 'en_US.UTF-8')

    # TODO find correct way to set system locale without user authentication
    _exec(['localectl', '--no-ask-password', 'set-locale', f'LANG={locale}'])


def set_system_formats(locale, formats_label):
    config.set('formats', (locale, formats_label))
    _exec(['gsettings', 'set', 'org.gnome.system.locale',
          'region', f"'{locale}'"])


def set_system_timezone(timezone):
    config.set('timezone', timezone)
    # TODO find correct way to set timezone without user authentication
    Popen(['timedatectl', '--no-ask-password', 'set-timezone', timezone])


def start_system_timesync():
    # TODO find correct way to set enable time sync without user authentication
    Popen(['timedatectl', '--no-ask-password', 'set-ntp', 'true'])
    Popen(['gsettings', 'set', 'org.gnome.desktop.datetime',
          'automatic-timezone', 'true'])
