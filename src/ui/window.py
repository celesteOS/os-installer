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


class Navigation:
    current: int = -1
    earliest: int = 0
    furthest: int = 0

    def set(self, state: int):
        self.current = state
        self.furthest = max(self.furthest, state)

    def is_not_earliest(self):
        return self.current > self.earliest

    def is_not_furthest(self):
        return self.current < self.furthest


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/main_window.ui')
class OsInstallerWindow(Adw.ApplicationWindow):
    __gtype_name__ = __qualname__

    image_stack = Gtk.Template.Child()
    main_stack = Gtk.Template.Child()

    next_revealer = Gtk.Template.Child()
    previous_revealer = Gtk.Template.Child()
    reload_revealer = Gtk.Template.Child()

    current_page = None
    navigation_lock = Lock()
    navigation = Navigation()
    pages = []
    # stack of previous pages when changing pages by name
    previous_pages = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # set advancing functions in global state
        global_state.advance = self.advance
        global_state.retranslate_pages = self.retranslate_pages
        global_state.navigate_to_page = self.navigate_to_page
        global_state.reload_title_image = self._reload_title_image
        global_state.installation_failed = self.show_failed_page

        # determine available pages
        self._determine_available_pages()

        # initialize first available page
        self._initialize_page(*self.available_pages[0])

    def _determine_available_pages(self):
        # list page types tupled with condition on when to use
        pages = [
            # pre-installation section
            ('language', LanguagePage, self._offer_language_selection()),
            ('welcome', WelcomePage, global_state.get_config('welcome_page')['usage']),
            ('keyboard-overview', KeyboardOverviewPage, True),
            ('internet', InternetPage, global_state.get_config(
                'internet_connection_required')),
            ('disk', DiskPage, True),
            ('partition', PartitionPage, True),
            ('encrypt', EncryptPage, global_state.get_config('offer_disk_encryption')),
            ('confirm', ConfirmPage, exists('/etc/os-installer/scripts/install.sh')),
            # configuration section
            ('user', UserPage, not global_state.get_config('skip_user')),
            ('locale', LocalePage, not global_state.get_config('skip_locale')),
            ('software', SoftwarePage, global_state.get_config('additional_software')),
            ('feature', FeaturePage, global_state.get_config('additional_features')),
            # summary
            ('summary', SummaryPage, True),
            # installation
            ('install', InstallPage, True),
            # post-installation
            ('done', DonePage, True),
            ('restart', RestartPage, True),
            # pushable only
            ('format', FormatPage, not global_state.get_config('skip_locale')),
            ('timezone', TimezonePage, not global_state.get_config('skip_locale')),
            ('keyboard-layout', KeyboardLayoutPage, True),
            ('keyboard-language', KeyboardLanguagePage, True),
            ('failed', FailedPage, True)
        ]
        # filter out nonexistent pages
        self.available_pages = [(page_name, page_type)
                                for page_name, page_type, condition in pages if condition]

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

    def _initialize_page(self, page_name, page_type, by_name: bool = False):
        # only add permanent pages to page list
        if not by_name:
            self.pages.append(page_name)
        wrapper = PageWrapper(page_type())
        self.main_stack.add_named(wrapper, page_name)
        return wrapper

    def _remove_all_but_one_page(self, kept_page_name):
        for page_name in filter(None, self.pages):
            if page_name == kept_page_name:
                continue
            child = self.main_stack.get_child_by_name(page_name)
            child.get_page().unload()
            self.main_stack.remove(child)
            del child
        self.pages = [kept_page_name] if kept_page_name else []

    def _load_page(self, page_number: int):
        assert page_number >= 0, 'Tried to go to non-existent page (underflow)'
        page_name = self.available_pages[page_number][0]

        # unload old page
        if self.current_page:
            self.current_page.unload()

        if page_number > self.navigation.furthest:
            # new page
            wrapper = self._initialize_page(*self.available_pages[page_number])
        else:
            # load page
            wrapper = self.main_stack.get_child_by_name(page_name)

        self.current_page = wrapper.get_page()

        match self.current_page.load():
            case "load_prev":
                self._load_page(page_number - 1)
                return
            case "load_next":
                self._load_page(page_number + 1)
                return
            case "prevent_back_navigation":
                self._remove_all_but_one_page(page_name)
                self.navigation.earliest = page_number

        self.main_stack.set_visible_child(wrapper)
        self.navigation.set(page_number)
        self._reload_title_image()
        self._update_navigation_buttons()

    def _load_page_by_name(self, page_name: str) -> None:
        self.current_page.unload()

        wrapper = self.main_stack.get_child_by_name(page_name)
        if wrapper == None:
            # find page
            list = [type for name, type in self.available_pages if name == page_name]
            if len(list) > 0:
                wrapper = self._initialize_page(page_name, list[0], True)
            else:
                print(f'Page named {page_name} does not exist. Are you testing things and forgot to comment it back in?')
                return
        self.current_page = wrapper.get_page()
        self.current_page.load()
        self.main_stack.set_visible_child(wrapper)

        self._reload_title_image()
        self.previous_revealer.set_reveal_child(True)
        self.next_revealer.set_reveal_child(False)
        self.reload_revealer.set_reveal_child(self.current_page.can_reload)

    def _load_previous_page(self):
        assert len(self.previous_pages) > 0, 'Logic Error: No previous pages to go to!'

        self.current_page.unload()
        popped_page = self.current_page

        page_name = self.previous_pages.pop()
        previous_page = self.main_stack.get_child_by_name(page_name)
        self.current_page = previous_page.get_page()
        self.current_page.load()
        self.main_stack.set_visible_child(previous_page)

        self._reload_title_image()
        self._update_navigation_buttons()

        # delete popped page
        del popped_page

    def _reload_title_image(self):
        next_image_name = '1' if self.image_stack.get_visible_child_name() == '2' else '2'
        next_image = self.image_stack.get_child_by_name(next_image_name)
        image_source = self.current_page.image
        if isinstance(image_source, str):
            next_image.set_from_icon_name(image_source)
        elif isinstance(image_source, Path):
            next_image.set_from_file(str(image_source))
        else:
            print('Developer hint: invalid request to set title image')
            return # ignoring
        self.image_stack.set_visible_child_name(next_image_name)

    def _update_navigation_buttons(self):
        # backward
        show_backward = self.navigation.is_not_earliest()
        self.previous_revealer.set_reveal_child(show_backward)

        # forward
        show_forward = self.navigation.is_not_furthest()
        self.next_revealer.set_reveal_child(show_forward)

        # reload
        self.reload_revealer.set_reveal_child(self.current_page.can_reload)

    ### public methods ###

    def advance(self, page, allow_return: bool = True):
        with self.navigation_lock:
            # confirm calling page is current page to prevent incorrect navigation
            if page != None and page != self.current_page:
                return

            if self.previous_pages:
                if not allow_return:
                    return print('Logic Error: Returning unpreventable, page name mode')
                self._load_previous_page()
            else:
                if not allow_return:
                    self._remove_all_but_one_page(None)
                    self.navigation.earliest = self.navigation.current + 1

                self._load_page(self.navigation.current + 1)

    def retranslate_pages(self):
        with self.navigation_lock:
            self._remove_all_but_one_page("language")
            self.navigation.furthest = 0

    def navigate_backward(self):
        with self.navigation_lock:
            if self.previous_pages:
                self._load_previous_page()
            elif self.navigation.is_not_earliest():
                self._load_page(self.navigation.current - 1)

    def navigate_forward(self):
        with self.navigation_lock:
            if self.navigation.is_not_furthest():
                self._load_page(self.navigation.current + 1)

    def reload_page(self):
        with self.navigation_lock:
            if not self.current_page.can_reload:
                return
            match self.current_page.load():
                case "load_prev":
                    self._load_page(self.navigation.current - 1)
                case "load_next":
                    self._load_page(self.navigation.current + 1)
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
            self.navigation.earliest = len(self.available_pages)
            self._update_navigation_buttons()

    def navigate_to_page(self, page_name):
        with self.navigation_lock:
            self.previous_pages.append(self.main_stack.get_visible_child_name())
            self._load_page_by_name(page_name)
