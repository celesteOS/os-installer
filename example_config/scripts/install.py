#!/usr/bin/env python3

# This is an example installer script.
# The script gets called with the following environment variables set:
# OSI_DESKTOP             : Desktop keyword, or empty if 'desktop' was not configured
# OSI_LOCALE              : Locale to be used in the new system
# OSI_DEVICE_PATH         : Device path at which to install
# OSI_DEVICE_IS_PARTITION : 1 if the specified device is a partition (0 -> disk)
# OSI_DEVICE_EFI_PARTITION: Set if device is partition and system uses EFI boot.
# OSI_USE_ENCRYPTION      : 1 if the installation is to be encrypted
# OSI_ENCRYPTION_PIN      : The encryption pin to use (if encryption is set)

import os
import sys
from time import sleep

# sanity check that all variables were set

env_vars = [
    'OSI_DESKTOP',
    'OSI_LOCALE',
    'OSI_KEYBOARD_LAYOUT',
    'OSI_DEVICE_PATH',
    'OSI_DEVICE_IS_PARTITION',
    'OSI_DEVICE_EFI_PARTITION',
    'OSI_USE_ENCRYPTION',
    'OSI_ENCRYPTION_PIN',
]


def sanityCheck():
    for env in env_vars:
        if os.getenv(env) is None:
            print('Installer script called without all environment variables set!')
            sys.exit(1)


def printEnv():
    print('Environment variables:')
    for env in env_vars:
        print(f'{env:<25} {os.getenv(env)}')


def idleAround():
    # Pretending to do something
    print('Pretending to do something')

    for i in range(20):
        sleep(1)
        print(".", end="", flush=True)


if __name__ == '__main__':
    sanityCheck()
    print('Installation started.')
    print('')
    printEnv()
    idleAround()

    print('')
    print('Installation completed.')

    sys.exit(0)
