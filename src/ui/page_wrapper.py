# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk

from .config import config


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/widgets/page_wrapper.ui')
class PageWrapper(Adw.Bin):
    __gtype_name__ = __qualname__

    content = Gtk.Template.Child()

    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)

        self.page = page
        self.content.set_child(self.page)

    def cleanup(self):
        if hasattr(self.page, '__cleanup__'):
            self.page.__cleanup__()
        config.unsubscribe(self.page)

    def get_page(self):
        return self.page

    def replace_page(self, page):
        self.cleanup()
        self.content.set_child(page)
        del self.page
        self.page = page

    def image(self):
        return self.page.image
