# SPDX-License-Identifier: GPL-3.0-or-later

''' All calls to other programs are encapsulated here. '''

import locale as Locale
import os
from subprocess import Popen
import subprocess

from gi.repository import Gio

from .config import config
from .functions import execute


def _run_program(args):
    env = os.environ.copy()
    env["LANG"] = config.get('language_chosen').locale
    Popen(args, env=env)


class SystemCaller:
    def __init__(self, app_window):
        self.action_group = Gio.SimpleActionGroup()

        self._add_syscall_action('error-search', self._open_internet_search)
        self._add_syscall_action('manage-disks', self._open_disks)
        self._add_syscall_action('wifi-settings', self._open_wifi_settings)

        app_window.insert_action_group('external', self.action_group)

        config.subscribe('keyboard_layout', self._set_system_keyboard_layout)
        config.subscribe('language_chosen', self._set_system_language)

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

    def _set_system_keyboard_layout(self, keyboard):
        keyboard_layout, _ = keyboard
        execute(['gsettings', 'set', 'org.gnome.desktop.input-sources', 'sources',
                 f"[('xkb','{keyboard_layout}')]"])

    def _set_system_language(self, language_info):
        locale = language_info.locale

        if not Locale.setlocale(Locale.LC_ALL, locale):
            print(f'Could not set locale {locale}, falling back to English. '
                  'Developer hint: make sure you set up locales correctly.')
            Locale.setlocale(Locale.LC_ALL, 'en_US.UTF-8')

        # TODO find correct way to set system locale without user authentication
        execute(['localectl', '--no-ask-password', 'set-locale',
                 f'LANG={locale}'])


def set_system_formats(locale, formats_label):
    config.set('formats', (locale, formats_label))
    execute(['gsettings', 'set', 'org.gnome.system.locale', 'region',
             f"'{locale}'"])


def set_system_timezone(timezone):
    config.set('timezone', timezone)
    # TODO find correct way to set timezone without user authentication
    Popen(['timedatectl', '--no-ask-password', 'set-timezone', timezone])


def start_system_timesync():
    # TODO find correct way to set enable time sync without user authentication
    Popen(['timedatectl', '--no-ask-password', 'set-ntp', 'true'])
    Popen(['gsettings', 'set', 'org.gnome.desktop.datetime',
          'automatic-timezone', 'true'])
