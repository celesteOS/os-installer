# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from threading import Lock
from os.path import exists

from gi.repository import Gtk, Adw

from .global_state import global_state

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
from .widgets import PageWrapper

from .language_provider import language_provider
from .system_calls import set_system_language


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


forward = 1
backwards = -1


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/main_window.ui')
class OsInstallerWindow(Adw.ApplicationWindow):
    __gtype_name__ = __qualname__

    image_stack = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()

    next_revealer = Gtk.Template.Child()
    previous_revealer = Gtk.Template.Child()
    reload_revealer = Gtk.Template.Child()

    navigation_lock = Lock()
    pages = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # set advancing functions in global state
        global_state.advance = self.advance
        global_state.retranslate_pages = self.retranslate_pages
        global_state.navigate_to_page = self.navigate_to_page
        global_state.reload_title_image = self._reload_title_image
        global_state.installation_failed = self.show_failed_page

        self.previous_pages = []

        # determine available pages
        self._determine_available_pages()

        # initialize first available page
        self._load_next_page()

    def _determine_available_pages(self):
        # list page types tupled with condition on when to use
        pages = [
            # pre-installation section
            ('language', self._offer_language_selection()),
            ('welcome', global_state.get_config('welcome_page')['usage']),
            ('keyboard-overview', True),
            ('internet', global_state.get_config(
                'internet_connection_required')),
            ('disk', True),
            ('partition', True),
            ('encrypt', global_state.get_config('offer_disk_encryption')),
            ('confirm', exists('/etc/os-installer/scripts/install.sh')),
            # configuration section
            ('user', not global_state.get_config('skip_user')),
            ('locale', not global_state.get_config('skip_locale')),
            ('software', global_state.get_config('additional_software')),
            ('feature', global_state.get_config('additional_features')),
            # summary
            ('summary', True),
            # installation
            ('install', True),
            # post-installation
            ('done', True),
            ('restart', True),
            # pushable only
            ('format', not global_state.get_config('skip_locale')),
            ('timezone', not global_state.get_config('skip_locale')),
            ('keyboard-layout', True),
            ('keyboard-language', True),
            ('failed', True)
        ]
        # filter out nonexistent pages
        self.available_pages = [name for name, condition in pages if condition]

    def _offer_language_selection(self):
            # only initialize language page, others depend on chosen language
        if fixed_language := global_state.get_config('fixed_language'):
            if fixed_info := language_provider.get_fixed_language(fixed_language):
                set_system_language(fixed_info)
                return False
            else:
                print('Developer hint: defined fixed language not available')
                global_state.set_config('fixed_language', '')
        return True

    def _initialize_page(self, page_name):
        self.pages.append(page_name)
        wrapper = PageWrapper(page_name_to_type[page_name]())
        self.main_stack.add_named(wrapper, page_name)
        return wrapper

    def _remove_all_but_one_page(self, kept_page_name):
        for page_name in filter(None, self.pages):
            if page_name == kept_page_name:
                continue
            page = self.main_stack.get_child_by_name(page_name)
            page.unload()
            self.main_stack.remove(page)
            del page
        self.pages = [kept_page_name] if kept_page_name else []

    def _get_next_page_name(self, offset: int = forward):
        current_page_name = self.main_stack.get_visible_child_name()
        if not current_page_name:
            return self.available_pages[0]
        current_index = self.available_pages.index(current_page_name)
        return self.available_pages[current_index + offset]

    def _load_next_page(self, offset: int = forward):
        page_name = self._get_next_page_name(offset)

        # unload old page
        if current_page := self.main_stack.get_visible_child():
            current_page.unload()

        page_to_load = self.main_stack.get_child_by_name(page_name)
        if not page_to_load:
            page_to_load = self._initialize_page(page_name)

        match page_to_load.load():
            case "load_prev":
                self._load_next_page(offset=backwards)
                return
            case "pass":
                self._load_next_page(offset=offset)
                return
            case "prevent_back_navigation":
                self._remove_all_but_one_page(page_name)

        self.main_stack.set_visible_child(page_to_load)
        self._reload_title_image()
        self._update_navigation_buttons()

    def _load_page_by_name(self, page_name: str) -> None:
        if current_page := self.main_stack.get_visible_child():
            current_page.unload()

        page_to_load = self._initialize_page(page_name)
        page_to_load.load()
        self.main_stack.set_visible_child(page_to_load)

        self._reload_title_image()
        self._update_navigation_buttons()

    def _load_previous_page(self):
        assert self.previous_pages, 'Logic Error: No previous pages to go to!'

        popped_page = self.main_stack.get_visible_child()
        popped_page.unload()
        self.pages.pop()

        previous_page_name = self.previous_pages.pop()
        page_to_load = self.main_stack.get_child_by_name(previous_page_name)
        page_to_load.load()
        self.main_stack.set_visible_child(page_to_load)

        # delete popped page
        self.main_stack.remove(popped_page)
        del popped_page

        self._reload_title_image()
        self._update_navigation_buttons()

    def _reload_title_image(self):
        next_image_name = '1' if self.image_stack.get_visible_child_name() == '2' else '2'
        next_image = self.image_stack.get_child_by_name(next_image_name)
        current_page = self.main_stack.get_visible_child()
        image_source = current_page.image()
        if isinstance(image_source, str):
            next_image.set_from_icon_name(image_source)
        elif isinstance(image_source, Path):
            next_image.set_from_file(str(image_source))
        else:
            print('Developer hint: invalid request to set title image')
            return # ignoring
        self.image_stack.set_visible_child_name(next_image_name)

    def _current_is_first(self):
        page_name = self.main_stack.get_visible_child_name()
        return page_name == self.pages[0]

    def _current_is_last(self):
        page_name = self.main_stack.get_visible_child_name()
        return page_name == self.pages[-1]

    def _update_navigation_buttons(self):
        self.previous_revealer.set_reveal_child(not self._current_is_first())
        self.next_revealer.set_reveal_child(not self._current_is_last())
        current_page = self.main_stack.get_visible_child()
        self.reload_revealer.set_reveal_child(current_page.can_reload())

    ### public methods ###

    def advance(self, page, allow_return: bool = True):
        with self.navigation_lock:
            # confirm calling page is current page to prevent incorrect navigation
            current_page = self.main_stack.get_visible_child()
            if page != None and page != current_page.get_page():
                return

            if self.previous_pages:
                if not allow_return:
                    return print('Logic Error: Returning unpreventable, page name mode')
                self._load_previous_page()
            else:
                if not allow_return:
                    self._remove_all_but_one_page(None)

                self._load_next_page()

    def retranslate_pages(self):
        with self.navigation_lock:
            self._remove_all_but_one_page("language")

    def navigate_backward(self):
        with self.navigation_lock:
            if self.previous_pages:
                self._load_previous_page()
            elif not self._current_is_first():
                self._load_next_page(backwards)

    def navigate_forward(self):
        with self.navigation_lock:
            if not self._current_is_last():
                self._load_next_page()

    def reload_page(self):
        with self.navigation_lock:
            current_page = self.main_stack.get_visible_child()
            if not current_page.can_reload():
                return
            match current_page.load():
                case "load_prev":
                    self._load_next_page(backwards)
                case "load_next":
                    self._load_next_page()
                # ignore case "prevent_back_navigation"

    def show_about_page(self):
        with self.navigation_lock:
            builder = Gtk.Builder.new_from_resource('/com/github/p3732/os-installer/ui/about_dialog.ui')
            popup = builder.get_object('about_window')
            popup.present(self)

    def show_confirm_quit_dialog(self, quit_callback):
        with self.navigation_lock:
            builder = Gtk.Builder.new_from_resource('/com/github/p3732/os-installer/ui/confirm_quit_dialog.ui')
            popup = builder.get_object('popup')
            popup.connect('response',
                          lambda _, response: quit_callback() if response == "stop" else None)
            popup.present(self)

    def show_failed_page(self):
        with self.navigation_lock:
            global_state.installation_running = False

            self._load_page_by_name('failed')
            self._update_navigation_buttons()

    def navigate_to_page(self, page_name):
        with self.navigation_lock:
            self.previous_pages.append(self.main_stack.get_visible_child_name())
            self._load_page_by_name(page_name)
