# SPDX-License-Identifier: GPL-3.0-or-later

from locale import gettext as _
from threading import Lock
from os.path import exists

from gi.repository import Gio, Gtk, Adw

from .config import config
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
from .widgets import LabeledImage, PageWrapper

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

page_name_to_title = {
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

non_returnable_pages = ['done', 'failed', 'install', 'restart', 'summary']


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

        self._setup_actions()
        self.connect("close-request", self._show_confirm_dialog, None)

        # set advancing functions in global state
        global_state.advance = self.advance
        global_state.retranslate_pages = self.retranslate_pages
        global_state.navigate_to_page = self.navigate_to_page
        global_state.reload_title_image = self._reload_title_image

        self.previous_pages = []

        # determine available pages
        self._determine_available_pages()

        # initialize first available page
        self._load_next_page()

    def _add_action(self, action_name, callback, keybinding):
        action = Gio.SimpleAction.new(action_name, None)
        action.connect('activate', callback)
        self.action_group.add_action(action)

        trigger = Gtk.ShortcutTrigger.parse_string(keybinding)
        named_action = Gtk.NamedAction.new(f'win.{action_name}')
        shortcut = Gtk.Shortcut.new(trigger, named_action)
        self.shortcut_controller.add_shortcut(shortcut)

    def _setup_actions(self):
        self.action_group = Gio.SimpleActionGroup()
        self.shortcut_controller = Gtk.ShortcutController()
        self.shortcut_controller.set_scope(Gtk.ShortcutScope(1))

        self._add_action('next-page', self._navigate_forward, '<Alt>Right')
        self._add_action('previous-page', self._navigate_backward, '<Alt>Left')
        self._add_action('reload-page', self._reload_page, 'F5')
        self._add_action('about-page', self._show_about_page, '<Alt>Return')
        self._add_action('quit', self._show_confirm_dialog, '<Ctl>q')

        if config.get('test_mode'):
            def show_failed(self, _, __): return self._load_page('failed')
            self._add_action('fail-page', show_failed, '<Alt>F')

        self.insert_action_group('win', self.action_group)
        self.add_controller(self.shortcut_controller)

    def _determine_available_pages(self):
        # list page types tupled with condition on when to use
        pages = [
            # pre-installation section
            ('language', self._offer_language_selection()),
            ('welcome', config.get('welcome_page')['usage']),
            ('keyboard-overview', True),
            ('internet', config.get(
                'internet_connection_required')),
            ('disk', True),
            ('partition', True),
            ('encrypt', config.get('offer_disk_encryption')),
            ('confirm', exists('/etc/os-installer/scripts/install.sh')),
            # configuration section
            ('user', not config.get('skip_user')),
            ('locale', not config.get('skip_locale')),
            ('software', config.get('additional_software')),
            ('feature', config.get('additional_features')),
            # summary
            ('summary', True),
            # installation
            ('install', True),
            # post-installation
            ('done', True),
            ('restart', True),
        ]
        # filter out nonexistent pages
        self.available_pages = [name for name, condition in pages if condition]

    def _offer_language_selection(self):
            # only initialize language page, others depend on chosen language
        if fixed_language := config.get('fixed_language'):
            if fixed_info := language_provider.get_fixed_language(fixed_language):
                config.set('language', (fixed_info.language_code, fixed_info.name))
                set_system_language(fixed_info)
                return False
            else:
                print('Developer hint: defined fixed language not available')
                config.set('fixed_language', '')
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

    def _load_page(self, page_name: str, offset: int = forward):
        if current_page := self.main_stack.get_visible_child():
            current_page.unload()

        if page_name in non_returnable_pages:
            self._remove_all_but_one_page(None)

        page_to_load = self.main_stack.get_child_by_name(page_name)
        if not page_to_load:
            page_to_load = self._initialize_page(page_name)

        match page_to_load.load():
            case "load_prev":
                self._load_next_page(backwards if offset > 0 else offset - 1)
                return
            case "pass":
                self._load_next_page(offset + (1 if offset > 0 else -1))
                return

        self.main_stack.set_visible_child(page_to_load)
        self._reload_title_image()
        self._update_navigation_buttons()

    def _load_next_page(self, offset: int = forward):
        page_name = self._get_next_page_name(offset)
        self._load_page(page_name, offset)

    def _load_previous_page(self):
        assert self.previous_pages, 'Logic Error: No previous pages to go to!'

        popped_page = self.main_stack.get_visible_child()
        self.pages.pop()

        # delete popped page
        popped_page.unload()
        self.main_stack.remove(popped_page)
        del popped_page

        previous_page_name = self.previous_pages.pop()
        self._load_page(previous_page_name)

    def _create_title(self):
        current_page_name = self.main_stack.get_visible_child_name()
        title = page_name_to_title[current_page_name]
        icon_name = page_name_to_image[current_page_name]

        if title == None:
            assert current_page_name == 'partition'
            label = self.main_stack.get_visible_child().get_page().get_title()
        else:
            label = _(title)

        if icon_name == None:
            current_page = self.main_stack.get_visible_child()
            icon_name = current_page.image()

        return LabeledImage(icon_name, label)

    def _reload_title_image(self):
        current_name = self.image_stack.get_visible_child_name()
        other_name = '1' if current_name == '2' else '2'
        other_page = self.image_stack.get_child_by_name(other_name)

        if other_page:
            self.image_stack.remove(other_page)

        title = self._create_title()
        self.image_stack.add_named(title, other_name)
        self.image_stack.set_visible_child_name(other_name)

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

    ### callbacks ###

    def _navigate_backward(self, _, __):
        with self.navigation_lock:
            if self.previous_pages:
                self._load_previous_page()
            elif not self._current_is_first():
                self._load_next_page(backwards)

    def _navigate_forward(self, _, __):
        with self.navigation_lock:
            if not self._current_is_last():
                self._load_next_page()

    def _reload_page(self, _, __):
        with self.navigation_lock:
            current_page = self.main_stack.get_visible_child()
            if not current_page.can_reload():
                return
            match current_page.load():
                case "load_prev":
                    self._load_next_page(backwards)
                case "load_next":
                    self._load_next_page()

    def _show_about_page(self, _, __):
        with self.navigation_lock:
            builder = Gtk.Builder.new_from_resource(
                '/com/github/p3732/os-installer/ui/about_dialog.ui')
            popup = builder.get_object('about_window')
            popup.present(self)

    def _show_confirm_dialog(self, _, __):
        def check_quit(_, response, self):
            if response == 'stop':
                self.get_application().quit()

        if not config.get('installation_running'):
            self.get_application().quit()
            return False

        with self.navigation_lock:
            builder = Gtk.Builder.new_from_resource(
                '/com/github/p3732/os-installer/ui/confirm_quit_dialog.ui')
            popup = builder.get_object('popup')
            popup.connect('response', check_quit, self)
            popup.present(self)

        return True

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
                next_page_name = self._get_next_page_name()
                if not allow_return:
                    self._remove_all_but_one_page(None)
                self._load_page(next_page_name)

    def retranslate_pages(self):
        with self.navigation_lock:
            self._remove_all_but_one_page("language")

    def navigate_to_page(self, page_name):
        with self.navigation_lock:
            self.previous_pages.append(self.main_stack.get_visible_child_name())
            self._load_page(page_name)
