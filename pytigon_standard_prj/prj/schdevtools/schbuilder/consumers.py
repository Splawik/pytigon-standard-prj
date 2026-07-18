import os
import sys
import asyncio


from channels.generic.websocket import AsyncJsonWebsocketConsumer


import psutil
from os import environ
from django.conf import settings


class Clock(AsyncJsonWebsocketConsumer):
    COUNT = 1

    async def connect(self):
        await self.accept()

    async def receive_json(self, content):
        await self.send_json({"txt": "hello world"})

        for i in range(10):
            await asyncio.sleep(1)
            await self.send_json({"clock": self.COUNT})
            self.COUNT += 1

    async def disconnect(self, close_code):
        pass


class WebServer(AsyncJsonWebsocketConsumer):
    PROC = None

    async def connect(self):
        await self.accept()

    async def _cleanup_proc(self):
        if self.PROC:
            try:
                parent = psutil.Process(self.PROC.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, ProcessLookupError):
                pass
            try:
                await self.PROC.wait()
            except Exception:
                pass
            self.PROC = None

    async def subprocess(self, prj):
        environ["PYTHONPATH"] = os.path.join(settings.ROOT_PATH, "..")

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pytigon.ptig",
            "manage_" + prj,
            "runserver",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.PROC = proc

        while True:
            data = await proc.stdout.readline()
            if data == b"":
                break
            await self.send_json({"txt": data.decode("utf-8")})

        await proc.wait()
        await self.send_json({"txt": ""})

    async def receive_json(self, content):
        command = content["command"]
        if command == "start":
            await self._cleanup_proc()
            loop = asyncio.get_running_loop()
            tsk = loop.create_task(self.subprocess(content["id"]))
            tsk.add_done_callback(lambda t: None)
        elif command == "stop":
            await self._cleanup_proc()

    async def disconnect(self, close_code):
        pass


class DjangoManage(AsyncJsonWebsocketConsumer):
    PROCS = []

    async def connect(self):
        await self.accept()

    async def subprocess(self, prj, cmd):
        environ["PYTHONPATH"] = os.path.join(settings.ROOT_PATH, "..")

        proc = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "pytigon.ptig",
            "manage_" + prj,
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.PROCS.append(proc)

        while True:
            data = await proc.stdout.readline()
            if data == b"":
                break
            await self.send_json({"txt": data.decode("utf-8")})

        await proc.wait()
        await self.send_json({"txt": ""})
        self.PROCS.remove(proc)

    async def receive_json(self, content):
        command = content["command"]
        if command == "start":
            cmd = content["cmd"].split(" ")
            loop = asyncio.get_running_loop()
            tsk = loop.create_task(self.subprocess(content["id"], cmd))
            tsk.add_done_callback(lambda t: None)
        elif command == "stop":
            for proc in list(self.PROCS):
                try:
                    parent = psutil.Process(proc.pid)
                    for child in parent.children(recursive=True):
                        child.kill()
                except (psutil.NoSuchProcess, ProcessLookupError):
                    pass
                try:
                    await proc.wait()
                except Exception:
                    pass
            self.PROCS.clear()

    async def disconnect(self, close_code):
        pass
