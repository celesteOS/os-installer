# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Condition, Lock, Thread

from gi.repository import Gtk

from .config import config
from .slideshow_provider import slideshow_provider


@Gtk.Template(resource_path='/com/github/p3732/os-installer/ui/pages/install.ui')
class InstallPage(Gtk.Box):
    __gtype_name__ = __qualname__

    stack = Gtk.Template.Child()
    carousel = Gtk.Template.Child()

    def __init__(self, **kwargs):
        Gtk.Box.__init__(self, **kwargs)

        if slideshow := slideshow_provider.get_slideshow():
            self.stack.set_visible_child_name('slideshow')
            self._setup_slideshow(slideshow)
        else:
            self.stack.set_visible_child_name('spinner')

    def _setup_slideshow(self, slideshow):
        self.num_slides = len(slideshow)
        self.durations = []
        self.slideshow_position = 0

        for slide in slideshow:
            picture = Gtk.Picture.new_for_paintable(slide.image)
            picture.add_css_class('card')
            picture.set_valign(Gtk.Align.CENTER)
            self.carousel.append(picture)
            self.durations.append(slide.duration)

        self.lock = Lock()
        self.cv = Condition(self.lock)

        self.stop_slideshow = False
        self.reset_timeout = False
        self.extra_timeout = 0
        self.current_pos = 0

        self.thread = Thread(target=self._show_next_slide, daemon=True)
        self.thread.start()
        config.subscribe('displayed-page', self._stop_thread, delayed=True)

    def _show_next_slide(self):
        with self.cv:
            while True:
                if self.current_pos < 0:
                    self.current_pos = int(self.carousel.get_position())

                timeout = self.durations[self.current_pos] + self.extra_timeout
                self.cv.wait(timeout=timeout)

                if self.stop_slideshow:
                    break
                elif self.reset_timeout:
                    self.reset_timeout = False
                    continue

                next_position = (self.current_pos + 1) % self.num_slides
                next_page = self.carousel.get_nth_page(next_position)
                self.carousel.scroll_to(next_page, True)
                self.current_pos = int(next_position)

    def _stop_thread(self, value):
        _, page = value
        # Relevant page change comes from scripting where page is None
        if page is None:
            self.stop_slideshow = True
            with self.cv:
                self.cv.notify_all()
            self.thread.join()

    ### callbacks ###

    @Gtk.Template.Callback('page_changed')
    def _page_changed(self, page, position):
        if position == self.current_pos:
            return

        with self.cv:
            self.current_pos = -1
            self.reset_timeout = True
            self.extra_timeout = 0
            self.cv.notify_all()
