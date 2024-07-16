# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

from .config import config

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


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/page_wrapper.ui')
class PageWrapper(Adw.Bin):
    __gtype_name__ = __qualname__

    content = Gtk.Template.Child()

    def __init__(self, page_name, **kwargs):
        super().__init__(**kwargs)

        self.page = page_name_to_type[page_name]()
        self.content.set_child(self.page)

    def cleanup(self):
        if hasattr(self.page, '__cleanup__'):
            self.page.__cleanup__()
        config.unsubscribe(self.page)

    def get_page(self):
        return self.page

    def replace_page(self, page_name):
        self.cleanup()
        new_page = page_name_to_type[page_name]()
        self.content.set_child(new_page)
        del self.page
        self.page = new_page

    def image(self):
        return self.page.image
