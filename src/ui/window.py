# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock
from os.path import exists

from gi.repository import Gio, Gtk, Adw

from .config import config
from .global_state import global_state

from .page_wrapper import PageWrapper

from .language_provider import language_provider
from .system_calls import set_system_language


non_returnable_pages = ['done', 'failed', 'install', 'restart', 'summary']


forward = 1
backwards = -1


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/main_window.ui')
class OsInstallerWindow(Adw.ApplicationWindow):
    __gtype_name__ = __qualname__

    navigation_view = Gtk.Template.Child()

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

        self._determine_available_pages()
        self._initialize_first_page()
        self.navigation_view.connect('popped', self._popped_page)
        self.navigation_view.connect('pushed', self._pushed_page)

    def _popped_page(self, _, __):
        self._update_page()

    def _pushed_page(self, _):
        self._update_page()

    def _initialize_first_page(self):
        self._remove_all_but_one_page(None)
        page_name = self.available_pages[0]
        initial_page = PageWrapper(page_name)
        self.navigation_view.replace([initial_page])
        self.pages = [page_name]

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
            def show_failed(_, __): return self._load_page('failed')
            self._add_action('fail-page', show_failed, '<Alt>F')
            def skip_page(_, __): return self.advance(None)
            self._add_action('skip', skip_page, '<Alt>S')

        self.insert_action_group('win', self.action_group)
        self.add_controller(self.shortcut_controller)

    def _determine_available_pages(self):
        # list page types tupled with condition on when to use
        pages = [
            # pre-installation section
            ('language', self._offer_language_selection()),
            ('welcome', config.get('welcome_page')['usage']),
            ('keyboard-overview', True),
            ('internet', config.get('internet_connection_required')),
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
                config.set('language',
                           (fixed_info.language_code, fixed_info.name))
                set_system_language(fixed_info)
                return False
            else:
                print('Developer hint: defined fixed language not available')
                config.set('fixed_language', '')
        return True

    def _remove_all_but_one_page(self, kept_page_name):
        for page_name in filter(None, self.pages):
            if page_name == kept_page_name:
                continue
            page = self.navigation_view.find_page(page_name)
            if not page:
                continue
            self.navigation_view.remove(page)
            del page
        self.pages = [kept_page_name] if kept_page_name else []
        self.previous_pages = []

    def _get_next_page_name(self, offset: int = forward):
        current_page = self.navigation_view.get_visible_page()
        current_index = self.available_pages.index(current_page.get_tag())
        return self.available_pages[current_index + offset]

    def _load_page(self, page_name: str, offset: int = forward):
        if page_name in non_returnable_pages:
            self._remove_all_but_one_page(None)

        page_to_load = self.navigation_view.find_page(page_name)
        if not page_to_load:
            page_to_load = PageWrapper(page_name)
            self.navigation_view.add(page_to_load)
            self.navigation_view.push_by_tag(page_name)
            self.pages.append(page_name)
        else:
            if offset >= forward:
                self.navigation_view.push_by_tag(page_name)
            else:
                self.navigation_view.pop_to_tag(page_name)

        match config.steal('page_navigation'):
            case 'load_prev':
                self._load_next_page(offset)
                return
            case 'pass':
                self._load_next_page(offset)
                return
        self._update_page()

    def _update_page(self):
        current_page = self.navigation_view.get_visible_page()
        is_first, is_last = self._current_is_first(), self._current_is_last()
        current_page.update_navigation_buttons(is_first, is_last)

    def _load_next_page(self, offset: int = forward):
        page_name = self._get_next_page_name(offset)
        self._load_page(page_name, offset)

    def _load_previous_page(self):
        assert self.previous_pages, 'Logic Error: No previous pages to go to!'

        popped_page = self.navigation_view.get_visible_page()
        self.navigation_view.pop()
        del popped_page

        previous_page_name = self.previous_pages.pop()
        self._load_page(previous_page_name, offset=backwards)

    def _current_is_first(self):
        page = self.navigation_view.get_visible_page()
        return page.get_tag() == self.pages[0]

    def _current_is_last(self):
        page_name = self.navigation_view.get_visible_page().get_tag()
        return page_name == self.pages[-1]

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
            self.navigation_view.get_visible_page().reload()

            match config.steal('page_navigation'):
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
            current_page = self.navigation_view.get_visible_page()
            if page != None and not current_page.has_same_type(page):
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
            self.previous_pages.append(
                self.navigation_view.get_visible_page().get_tag())
            self._load_page(page_name)
