import os
import sys
import time

import watchdog.events
import watchdog.observers


class Handler(watchdog.events.PatternMatchingEventHandler):

    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path)
        # Event is created, you can process it now

    def on_modified(self, event):
        print("Watchdog received modified event - % s." % event.src_path)
        # Event is modified, you can process it now


def watch_winform(path: str, event_handler, stopped):
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            if stopped.isSet():
                print("stopped watch dog!!!")
                return 0
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def watch(path: str, handler):
    event_handler = handler
    observer = watchdog.observers.Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    src_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    hand = Handler()
    watch(src_path, hand)
