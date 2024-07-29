# SPDX-License-Identifier: GPL-3.0-or-later

from threading import Lock

from .global_state import global_state


class Preloadable:
    def __init__(self, preload_func):
        self.preload_func = preload_func
        self.preload_started = False
        self.preloaded = False
        self.preloading_lock = Lock()

    ### public methods ###

    def assert_preloaded(self):
        if self.preloaded:
            return

        with self.preloading_lock:
            if self.preloaded:
                return

            if not self.preload_started:
                class_name = self.__class__.__name__
                print(f'Preloading for {class_name} was never started')
                self.preloading_lock.release()
                self.preload()
                self.preloading_lock.acquire()

            # await result
            self.future.result()
            self.preloaded = True

    def preload(self):
        with self.preloading_lock:
            if self.preload_started:
                return

            self.future = global_state.thread_pool.submit(self.preload_func)
            self.preload_started = True
