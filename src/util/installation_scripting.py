# SPDX-License-Identifier: GPL-3.0-or-later

from enum import Enum
from threading import Lock
import os

from gi.repository import Gio, GLib, Vte

from .global_state import global_state


class Step(Enum):
    none = 0
    prepare = 1
    install = 2
    configure = 3
    done = 4


class InstallationScripting():
    '''
    Handles all calls to scripts for installation. The installation process consists of 3 steps:
    * Preparation. Used e.g. for updating mirrors.
    * Installation. Installs an OS onto a disk.
    * Configuration. Configures an OS according to user's choices.
    '''

    def __init__(self):
        self.terminal = self._setup_terminal()
        self.cancel = Gio.Cancellable()

        self.lock = Lock()
        self.ready_step = Step.none
        self.running_step = Step.none
        self.finished_step = Step.none

    def _setup_terminal(self):
        terminal = Vte.Terminal()
        terminal.set_input_enabled(False)
        terminal.set_scroll_on_output(True)
        terminal.set_hexpand(True)
        terminal.set_vexpand(True)
        terminal.connect('child-exited', self._on_child_exited)
        return terminal

    def _try_start_next_script(self):
        if self.running_step != Step.none:
            return

        if self.finished_step.value >= self.ready_step.value:
            return

        next_step = Step(self.finished_step.value + 1)
        print(f'Starting step "{next_step.name}"...')

        with_install_env = next_step is Step.install or next_step is Step.configure
        with_configure_env = next_step is Step.configure
        envs = global_state.create_envs(with_install_env, with_configure_env)

        # check config
        if envs == None:
            print(f'Not all config options set for "{next_step.name}". '
                  'Please report this bug.')
            print('############################')
            print(global_state.config)
            print('############################')
            global_state.installation_failed()
            return

        # start script
        file_name = f'/etc/os-installer/scripts/{next_step.name}.sh'
        if os.path.exists(file_name):
            started_script, _ = self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT, '/', ['sh', file_name],
                envs, GLib.SpawnFlags.DEFAULT, None, None, self.cancel)
            if not started_script:
                print(f'Could not start {self.finished_step.name} script! '
                      'Ignoring.')
                self._try_start_next_script()
            else:
                self.running_step = next_step
        else:
            print(f'No script for step {next_step.name} exists.')
            self.finished_step = next_step
            self._try_start_next_script()

    ### callbacks ###

    def _on_child_exited(self, terminal, status):
        with self.lock:
            self.finished_step = self.running_step
            self.running_step = Step.none

            if not status == 0 and not global_state.demo_mode:
                print(f'Failure during step "{self.finished_step.name}"')
                global_state.installation_failed()
                return

            print(f'Finished step "{self.finished_step.name}".')

            if self.finished_step is Step.configure:
                global_state.installation_running = False
                global_state.advance(None, allow_return=False)
            else:
                self._try_start_next_script()

    ### public methods ###

    def set_ok_to_start_step(self, step: Step):
        with self.lock:
            if self.ready_step.value < step.value:
                self.ready_step = step
                self._try_start_next_script()


installation_scripting = InstallationScripting()
