"""Local-only FastF1 browser login; no credentials or tokens reach Streamlit."""
import re
import subprocess
import sys
import threading
import time


class F1Login:
    def __init__(self):
        self.process = None
        self.url = None
        self.started = 0.0
        self.lock = threading.RLock()

    def connected(self):
        # FastF1 3.9 keeps the shared local account token in its own storage.
        try:
            from fastf1.internals.f1account import token_manager
            token = token_manager.get_stored()
            return token is not None and token.is_valid()
        except (ImportError, OSError, ValueError):
            return False

    def start(self):
        with self.lock:
            if self.running():
                return
            self.url = None
            self.process = subprocess.Popen(
                [sys.executable, '-u', '-m', 'fastf1', 'auth', 'f1tv', '--authenticate', '--method', 'browser'],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True,
            )
            self.started = time.monotonic()
            threading.Thread(target=self._read_url, args=(self.process,), daemon=True).start()
            threading.Thread(target=self._expire, args=(self.process,), daemon=True).start()

    def _read_url(self, process):
        try:
            for line in process.stdout:
                match = re.search(r'https://f1login\.fastf1\.dev\?port=([0-9]+)', line)
                if match and 0 < int(match[1]) < 65536:
                    with self.lock:
                        if self.process is process:
                            self.url = match[0]
        finally:
            process.stdout.close()

    def _expire(self, process):
        try:
            process.wait(timeout=300)
        except subprocess.TimeoutExpired:
            with self.lock:
                if self.process is process:
                    self.cancel()

    def running(self):
        return self.process is not None and self.process.poll() is None

    def cancel(self):
        with self.lock:
            if self.running():
                self.process.terminate()
            self.url = None

    def disconnect(self):
        self.cancel()
        from fastf1.internals.f1account import clear_token
        clear_token()
