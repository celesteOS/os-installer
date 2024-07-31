# SPDX-License-Identifier: GPL-3.0-or-later

from locale import gettext as _

from gi.repository import Adw, Gtk

from .config import config
from .widgets import LabeledImage

from .choices import FeaturePage, SoftwarePage
from .confirm import ConfirmPage
from .disk import DiskPage
from .done import DonePage
from .encrypt import EncryptPage
from .failed import FailedPage
from .filter import FormatPage, TimezonePage
from .install import InstallPage
from .internet import InternetPage
from .keyboard import KeyboardLanguagePage, KeyboardLayoutPage, KeyboardOverviewPage
from .language import LanguagePage
from .locale import LocalePage
from .partition import PartitionPage
from .restart import RestartPage
from .summary import SummaryPage
from .user import UserPage
from .welcome import WelcomePage

page_name_to_caption = {
    # Translators: Page title
    'confirm':              _('Confirmation'),
    # Translators: Page title
    'disk':                 _('Disk Selection'),
    # Translators: Page title
    'done':                 _('Installation Complete'),
    # Translators: Page title
    'encrypt':              _('Disk Encryption'),
    # Translators: Page title
    'failed':               _('Installation Failed'),
    # Translators: Page title
    'feature':              _('Additional Features'),
    # Translators: Page title
    'format':               _('Select Region'),
    # Translators: Page title
    'install':              _('Installing'),
    # Translators: Page title
    'internet':             _('Internet Connection Check'),
    # Translators: Page title
    'keyboard-language':    _('Keyboard Language'),
    # Translators: Page title
    'keyboard-layout':      _('Keyboard Layout Selection'),
    # Translators: Page title
    'keyboard-overview':    _('Keyboard Layout'),
    # Language page has no title
    'language':             '',
    # Translators: Page title
    'locale':               _('Adapt to Location'),
    # Special-cased: Partition page shows disk name as title
    'partition':            None,
    # Translators: Page title
    'restart':              _('Restarting'),
    # Translators: Page title
    'software':             _('Additional Software'),
    # Translators: Page title
    'summary':              _('Summary'),
    # Translators: Page title
    'timezone':             _('Select Location'),
    # Translators: Page title
    'user':                 _('User Account'),
    # Translators: Page title
    'welcome':              _('Welcome'),
}

page_name_to_image = {
    'confirm':              'question-round-symbolic',
    'disk':                 None,
    'done':                 'success-symbolic',
    'encrypt':              'dialog-password-symbolic',
    'failed':               'computer-fail-symbolic',
    'feature':              'puzzle-piece-symbolic',
    'format':               'map-symbolic',
    'install':              'OS-Installer-symbolic',
    'internet':             None,
    'keyboard-language':    'input-keyboard-symbolic',
    'keyboard-layout':      'input-keyboard-symbolic',
    'keyboard-overview':    'input-keyboard-symbolic',
    'language':             'language-symbolic',
    'locale':               'globe-symbolic',
    'partition':            'drive-harddisk-system-symbolic',
    'restart':              'system-reboot-symbolic',
    'software':             'system-software-install-symbolic',
    'summary':              'checkbox-checked-symbolic',
    'timezone':             'map-symbolic',
    'user':                 'user-symbolic',
    'welcome':              None,
}

page_name_to_type = {
    'confirm':              ConfirmPage,
    'disk':                 DiskPage,
    'done':                 DonePage,
    'encrypt':              EncryptPage,
    'failed':               FailedPage,
    'feature':              FeaturePage,
    'format':               FormatPage,
    'install':              InstallPage,
    'internet':             InternetPage,
    'keyboard-language':    KeyboardLanguagePage,
    'keyboard-layout':      KeyboardLayoutPage,
    'keyboard-overview':    KeyboardOverviewPage,
    'language':             LanguagePage,
    'locale':               LocalePage,
    'partition':            PartitionPage,
    'restart':              RestartPage,
    'software':             SoftwarePage,
    'summary':              SummaryPage,
    'timezone':             TimezonePage,
    'user':                 UserPage,
    'welcome':              WelcomePage,
}

reloadable_pages = ['disk', 'partition']


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/page_wrapper.ui')
class PageWrapper(Adw.Bin):
    __gtype_name__ = __qualname__

    next_revealer = Gtk.Template.Child()
    previous_revealer = Gtk.Template.Child()
    title_stack = Gtk.Template.Child()
    reload_revealer = Gtk.Template.Child()

    content = Gtk.Template.Child()

    def __init__(self, page_name, **kwargs):
        super().__init__(**kwargs)
        self._set_new_page(page_name)

    def __del__(self):
        config.unsubscribe(self.page)
        del self.page

    def _set_new_page(self, page_name):
        self.page = page_name_to_type[page_name]()
        self.page_name = page_name
        self.content.set_child(self.page)
        self._reload_title()

    def _reload_title(self):
        current_name = self.title_stack.get_visible_child_name()
        other_name = '1' if current_name == '2' else '2'

        if other_title := self.title_stack.get_child_by_name(other_name):
            self.title_stack.remove(other_title)

        self.title_stack.add_named(self._get_title(), other_name)
        self.title_stack.set_visible_child_name(other_name)

    def _get_title(self):
        caption = page_name_to_caption[self.page_name]
        image = page_name_to_image[self.page_name]

        if caption == None:
            assert self.page_name == 'partition'
            caption = config.get('selected_disk').name
        # only translate translatable strings
        elif caption != "":
            caption = _(caption)

        if not image:
            image = self.page.image

        return LabeledImage(image, caption)

    ### public methods ###

    def get_page(self):
        return self.page

    def reload(self):
        if not self.page_name in reloadable_pages:
            return
        config.unsubscribe(self.page)
        del self.page
        self._set_new_page(self.page_name)

    def update_navigation_buttons(self, is_first: bool, is_last: bool):
        self.previous_revealer.set_reveal_child(not is_first)
        self.next_revealer.set_reveal_child(not is_last)
        self.reload_revealer.set_reveal_child(
            self.page_name in reloadable_pages)
