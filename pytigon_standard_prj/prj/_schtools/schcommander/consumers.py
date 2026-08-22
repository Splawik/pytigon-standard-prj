import asyncio
import getpass
import json
import os
import struct
import subprocess

from channels.generic.websocket import (
    AsyncWebsocketConsumer,
)

try:
    import fcntl
    import pty
    import termios
except ImportError:
    pass

from django.conf import settings
from pytigon_lib.schtools.tools import get_executable


class ShellConsumer(AsyncWebsocketConsumer):
    def set_winsize(self, fd, row, col, xpix=0, ypix=0):
        winsize = struct.pack("HHHH", row, col, xpix, ypix)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            x = json.loads(text_data)
            if "input" in x:
                if self.fd:
                    # Writing to PTY can theoretically block, but for small chunks of text
                    # os.write is safe. For a fully async approach, use loop.connect_write_pipe.
                    os.write(self.fd, x["input"].encode("utf-8"))
            if "resize" in x:
                size = x["resize"]
                if self.fd:
                    self.set_winsize(self.fd, size["rows"], size["cols"])
            if "ping" in x:
                await self.send(text_data="pong")

    async def connect(self):
        print("Connecting.......")
        self.fd = None
        self.child_pid = None
        await self.accept()

        (child_pid, fd) = pty.fork()
        if child_pid == 0:
            env2 = os.environ.copy()
            env2["TERM"] = "xterm"
            if (
                settings.PLATFORM_TYPE == "webserver"
                and getpass.getuser() == "www-data"
            ):
                env2["HOME"] = "/home/www-data"
            subprocess.run([get_executable(), "-m", "xonsh"], env=env2)
        else:
            self.fd = fd
            self.child_pid = child_pid

            # Register the file descriptor directly into the server's event loop (Granian/Uvicorn).
            # The read_and_forward_pty_output function will be triggered automatically when data arrives.
            self.loop = asyncio.get_running_loop()
            self.loop.add_reader(self.fd, self.read_and_forward_pty_output)

    def read_and_forward_pty_output(self):
        max_read_bytes = 1024 * 20
        try:
            output = os.read(self.fd, max_read_bytes)
            if not output:
                # Empty output means the shell process closed the stream
                self.loop.remove_reader(self.fd)
                print("Shell closed")
                return

            try:
                output_str = output.decode(errors="replace")
            except Exception:
                print("---------------------------------------------")
                print(output)
                print("---------------------------------------------")
                output_str = ""

            if output_str:
                # Since add_reader invokes a synchronous callback, we must schedule
                # the async send task (self.send) into the active event loop.
                asyncio.create_task(self.send(text_data=output_str))

        except Exception:
            # Handle potential exceptions when the descriptor is closed during disconnect
            self.loop.remove_reader(self.fd)

    async def disconnect(self, close_code):
        print("Disconnect.......")
        if self.fd:
            try:
                self.loop.remove_reader(self.fd)
                os.write(self.fd, b"exit\n")
                os.close(self.fd)
            except:
                pass
