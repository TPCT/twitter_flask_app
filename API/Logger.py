from threading import current_thread, enumerate, Lock
from time import strftime
from textwrap import fill


class Logger:
    def __init__(self, width=500, threads_locker=None):
        self.logger = None
        self.width = width

    def log(self, message, error=False):
        print(
            fill(f"[{' +' if not error else ' -'} {strftime('%Y/%m/%d %H:%M:%S')}]"
                 f"[{current_thread().name} / {len(enumerate())}] {message}",
                 self.width, subsequent_indent="\t", replace_whitespace=False))
