A simple operating system installer, intended to be used with live install systems.
It provides a GNOME Adwaita-style interface for:
* Bootstrapping: Language, keyboard, internet connection, disk selection, user configuration
* Customazibility: Welcome page, installation slideshow, additional software options, all fully translatable
* Over 25 translations

# Translations
<a href="https://hosted.weblate.org/engage/os-installer/">
<img src="https://hosted.weblate.org/widgets/os-installer/-/os-installer/multi-auto.svg" alt="Translation status" />
</a>

Help with translations is always welcome! The simplest way is via [__Weblate__](https://hosted.weblate.org/projects/os-installer/), which provides a very intuitive website.

Alternatively you could try the autonomous way:
* Fork, clone and build this repository.
* Add your [language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) `xx` to the `po/LINGUAS` file.
* Generate a new translation file with `ninja -C build os-installer-update-po` and [edit it](https://flathub.org/apps/org.gnome.Gtranslator).
* Test the translation, commit and push the changes to your fork and create a merge request. Thank you!

# Testing
Clone the project with [GNOME Builder](https://apps.gnome.org/Builder/) via `https://gitlab.gnome.org/p3732/os-installer.git` and run it (this will not make changes to your system).

## Development Setup
Install the dependencies: `blueprint-compiler gnome-desktop gtk4 libadwaita libgweather python-yaml udisks vte`.
Then clone and install:

```
git clone --recursive https://gitlab.gnome.org/p3732/os-installer.git
cd os-installer
meson setup build
sudo meson install -C build
```

To try OS-Installer, without modifying any system settings, run it in test mode with `os-installer -t`.
Running in GNOME Builder uses the demo mode (`os-installer -d`) and shows test dummy disks.
Uninstall with `sudo ninja -C build uninstall `

# Distributions
The following describes how to use this in a distribution.

## Configuration
Place a configuration and installation scripts under `/etc/os-installer` (or symlink it to another folder).
An example structure is given in the `example_config` folder,
where `config.yaml` is the config file.
In it scripts for up to 3 stages of an installation can be set:
* Preparation - Testing mirrors, package pre-fetching
* Installation - Bootstrap system and write to disk
* Configuration - Apply user choices to new system
Any later stage can do what a previous stage can do, so only the last one is needed.
The example scripts list which environment variables are made available to each script.

The scripts can be written in any language as long as a shell can correctly execute them.
Also, the installer will run scripts as the user it is started by.
If they require elevated priviledges (hint: they probably do),
these need to be granted to the script through other means.

## Dependencies
In addition to the dependencies listed under Development Setup,
the default OS-Installer config also expects these GNOME apps to be available:
`epiphany`, `gnome-disk-utility`, `gnome-control-center`
Alternatives can be specified in the config.

Similarly `systemd` is expected to be available, i.e. `localectl` and `timedatectl`.

## Examples
Example configurations of distributions (experimenting) with using OS-Installer:
* https://github.com/snowflakelinux/os-installer-snowflake-config (NixOS-based)
* https://github.com/arkanelinux/os-installer-config (Arch-based)

# Contact
There is a matrix room https://matrix.to/#/#os-installer:matrix.org in which you can ask questions.
Response time might vary.
