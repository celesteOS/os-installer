# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock
import os

from gi.repository import Gio, GLib, Vte

from .config import config
from .envvar_creator import create_envs
from .installation_step import InstallationStep
from .terminal_provider import terminal_provider


class InstallationScripting():
    '''
    Handles all calls to scripts for installation. The installation process consists of 3 steps:
    * Preparation. Used e.g. for updating mirrors.
    * Installation. Installs an OS onto a disk.
    * Configuration. Configures an OS according to user's choices.
    '''

    def __init__(self):
        self.cancel = Gio.Cancellable()

        self.lock = Lock()
        self.ready_step = InstallationStep.none
        self.running_step = InstallationStep.none
        self.finished_step = InstallationStep.none

    def _fail_installation(self):
        config.set('installation_running', False)
        config.set('displayed-page', 'failed')
        # Translators: Notification text
        config.set('send_notification', _("Installation Failed"))

    def _try_start_next_script(self):
        if self.running_step != InstallationStep.none:
            return

        if self.finished_step.value >= self.ready_step.value:
            return

        next_step = InstallationStep(self.finished_step.value + 1)
        if next_step != InstallationStep.prepare:
            config.set('installation_running', True)

        envs = create_envs(next_step)

        # start script
        file_name = config.get('scripts')[next_step.name]
        if file_name is not None and os.path.exists(file_name):
            print(f'Starting step "{next_step.name}"...')
            pty = Vte.Pty.new_sync(Vte.PtyFlags.NO_CTTY, self.cancel)
            pty.spawn_async(
                '/', ['sh', file_name], envs,
                GLib.SpawnFlags.DEFAULT,
                None, None, -1, self.cancel,
                self._on_child_spawned,
                (None,))
            terminal_provider.set_pty(pty)
            self.running_step = next_step
        elif file_name:
            print(f'Could not find configured script "{file_name}"')
            print('Stopping installation')
            self._fail_installation()
        else:
            print(f'Skipping step "{next_step.name}"')
            self.finished_step = next_step
            self._try_start_next_script()

    ### callbacks ###

    def _on_child_spawned(self, pty, task, data):
        success, pid = pty.spawn_finish(task)
        if success:
            GLib.child_watch_add(pid, self._on_child_exited, None)
        else:
            print(f'Error starting {self.running_step}')
            self._fail_installation()

    def _on_child_exited(self, pid, status, data):
        with self.lock:
            self.finished_step = self.running_step
            self.running_step = InstallationStep.none

            if not status == 0 and not config.get('demo_mode'):
                print(f'Failure during step "{self.finished_step.name}"')
                self._fail_installation()
                return

            print(f'Finished step "{self.finished_step.name}".')

            if self.finished_step is InstallationStep.configure:
                config.set('installation_running', False)
                # Translators: Notification text
                config.set('send_notification', _("Finished Installation"))
                config.set_next_page(None)
            else:
                self._try_start_next_script()

    def _set_ok_to_start_step(self, step: InstallationStep):
        with self.lock:
            if self.ready_step.value < step.value:
                self.ready_step = step
                self._try_start_next_script()

    ### public methods ###

    def can_run_configure(self):
        self._set_ok_to_start_step(InstallationStep.configure)

    def can_run_install(self):
        self._set_ok_to_start_step(InstallationStep.install)

    def can_run_prepare(self):
        self._set_ok_to_start_step(InstallationStep.prepare)


installation_scripting = InstallationScripting()
