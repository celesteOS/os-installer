# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock

from gi.repository import Adw, Gio, Gtk

from .config import config
from .page_wrapper import PageWrapper
from .state_machine import page_order, state_machine


class Navigation(Adw.Bin):
    __gtype_name__ = __qualname__

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.navigation_lock = Lock()
        self.navigation_view = Adw.NavigationView()
        self.navigation_view.set_pop_on_escape(False)
        self.set_child(self.navigation_view)

        self._determine_available_pages()
        self._initialize_first_page()
        self.navigation_view.connect('get-next-page', self._add_next_page)
        self.navigation_view.connect('popped', self._popped_page)
        self.navigation_view.connect('pushed', self._pushed_page)

        config.subscribe('displayed-page', self._change_page, delayed=True)

    def _get_next_page(self):
        if self._current_is_last():
            return None

        if next_page_name := self._get_next_page_name():
            return self.navigation_view.find_page(next_page_name)
        else:
            return None

    def _add_next_page(self, _):
        with self.navigation_lock:
            return self._get_next_page()

    def _popped_page(self, _, popped_page):
        if not popped_page.permanent:
            del popped_page
        self._update_page()

    def _pushed_page(self, _):
        self._update_page()

    def _initialize_first_page(self):
        initial_page = PageWrapper(self.available_pages[0])
        self.navigation_view.add(initial_page)

    def _determine_available_pages(self):
        page_conditions = {
            'language': self._offer_language_selection(),
            'welcome': config.get('welcome_page')['usage'],
            'internet': config.get('internet')['connection_required'],
            'encrypt': self._offer_encryption(),
            'desktop': config.get('desktop'),
            'confirm': config.get('scripts')['install'],
            'user': not config.get('skip_user'),
            'region': not config.get('skip_region'),
            'software': config.get('additional_software'),
            'feature': config.get('additional_features'),
        }

        self.available_pages = [
            page for page in page_order if page not in page_conditions or page_conditions[page]]

    def _offer_language_selection(self):
        use_fixed_language = config.get('language_use_fixed')
        if type(use_fixed_language) is not bool:
            use_fixed_language = use_fixed_language.result()
            config.set('language_use_fixed', use_fixed_language)
        return not use_fixed_language

    def _offer_encryption(self):
        encryption_settings = config.get('disk_encryption')
        if not encryption_settings['offered']:
            return False
        elif encryption_settings['forced'] and encryption_settings['generated']:
            config.set('use_encryption', True)
            return False
        else:
            return True

    def _remove_all_pages(self, exception=None):
        for page_name in self.available_pages:
            if page_name == exception:
                continue
            if page := self.navigation_view.find_page(page_name):
                self.navigation_view.remove(page)
                del page

        replacement = []
        if exception:
            replacement = [self.navigation_view.find_page(exception)]
        self.navigation_view.replace(replacement)

    def _get_next_page_name(self):
        current_page_name = self.navigation_view.get_visible_page_tag()
        current_index = self.available_pages.index(current_page_name)
        if (next_index := current_index + 1) < len(self.available_pages):
            return self.available_pages[next_index]
        else:
            return None

    def _advance_wrapper(self, page=None, dummy=None):
        with self.navigation_lock:
            self._advance(self, page)

    def _advance(self, page):
        # confirm calling page is current page to prevent incorrect navigation
        current_page = self.navigation_view.get_visible_page()
        if type(page) == PageWrapper and not current_page.has_same_type(page):
            return

        if not current_page.permanent:
            self.navigation_view.pop()
        else:
            next_page_name = self._get_next_page_name()
            match state_machine.transition(current_page.get_tag(), next_page_name):
                case 'no_return':
                    self._remove_all_pages()
                case 'retranslate':
                    self._remove_all_pages('language')

            self._load_page(next_page_name)

    def _load_page(self, page_name: str, permanent: bool = True):
        if self.navigation_view.find_page(page_name):
            # reuse existing page is still in stack
            self.navigation_view.push_by_tag(page_name)
        else:
            page_to_load = PageWrapper(page_name, permanent)

            if permanent:
                self.navigation_view.add(page_to_load)
                if self.navigation_view.get_visible_page_tag() != page_name:
                    self.navigation_view.push_by_tag(page_name)
            else:
                self.navigation_view.push(page_to_load)

        self._update_page()

    def _update_page(self):
        current_page = self.navigation_view.get_visible_page()
        is_first, is_last = self._current_is_first(), self._current_is_last()
        current_page.update_navigation_buttons(is_first, is_last)

    def _current_is_first(self):
        return len(self.navigation_view.get_navigation_stack()) == 1

    def _current_is_last(self):
        page = self.navigation_view.get_visible_page()
        if not page.permanent:
            return True
        page_index = self.available_pages.index(page.get_tag())
        if page_index + 1 == len(self.available_pages):
            return True
        next_page_name = self.available_pages[page_index + 1]
        return self.navigation_view.find_page(next_page_name) is None

    ### callbacks ###

    def _change_page(self, value):
        with self.navigation_lock:
            match value := config.steal('displayed-page'):
                case 'next', page:
                    self._advance(page)
                case _:
                    page_name = value
                    assert self.navigation_view.find_page(page_name) is None
                    self._load_page(page_name, permanent=False)

    ### public methods ###

    def advance(self, page=None):
        with self.navigation_lock:
            self._advance(page)

    def go_backward(self):
        with self.navigation_lock:
            self.navigation_view.pop()

    def go_forward(self):
        with self.navigation_lock:
            page_to_load = self._get_next_page()
            self.navigation_view.push(page_to_load)

    def reload_page(self):
        with self.navigation_lock:
            self.navigation_view.get_visible_page().reload()

    def show_failed(self):
        with self.navigation_lock:
            return self._load_page('failed', permanent=False)
