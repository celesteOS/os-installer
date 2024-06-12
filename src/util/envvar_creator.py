# SPDX-License-Identifier: GPL-3.0-or-later

from .installation_step import InstallationStep


def _get(config, var):
    if var not in config:
        print(f'Required variable {var} not set, using empty string fallback. '
              'Please report this error.')
        return ''
    else:
        value = config[var]
        if isinstance(value, bool):
            return 1 if value else 0
        else:
            return value


def create_envs(config, installation_step: InstallationStep):
    with_configure_envs = installation_step is InstallationStep.configure
    with_install_envs = installation_step is InstallationStep.install or with_configure_envs

    envs = []
    if with_install_envs:
        envs += [
            f'OSI_LOCALE={_get(config, "locale")}',
            f'OSI_KEYBOARD_LAYOUT={_get(config, "keyboard_layout_code")}',
            f'OSI_DEVICE_PATH={_get(config, "disk_device_path")}',
            f'OSI_DEVICE_IS_PARTITION={_get(config, "disk_is_partition")}',
            f'OSI_DEVICE_EFI_PARTITION={_get(config, "disk_efi_partition")}',
            f'OSI_USE_ENCRYPTION={_get(config, "use_encryption")}',
            f'OSI_ENCRYPTION_PIN={_get(config, "encryption_pin")}',
        ]

    if with_configure_envs:
        envs += [
            f'OSI_USER_NAME={_get(config, "user_name")}',
            f'OSI_USER_AUTOLOGIN={_get(config, "user_autologin")}',
            f'OSI_USER_PASSWORD={_get(config, "user_password")}',
            f'OSI_FORMATS={_get(config, "formats_locale")}',
            f'OSI_TIMEZONE={_get(config, "timezone")}',
            f'OSI_ADDITIONAL_SOFTWARE={_get(config, "chosen_software_packages")}',
            f'OSI_ADDITIONAL_FEATURES={_get(config, "chosen_feature_names")}',
        ]
    return envs + [None]
