from channels.generic.websocket import AsyncWebsocketConsumer


class teleconference(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_node = None

    async def connect(self):
        global GLOBAL_NODES
        slug = "default"

        await self.accept()

        if slug not in GLOBAL_NODES:
            GLOBAL_NODES[slug] = Node(slug, [self])
        else:
            GLOBAL_NODES[slug].clients.append(self)

        self.current_node = GLOBAL_NODES[slug]

        if len(self.current_node.clients) == 1:
            await self.send(text_data="owner")
        elif len(self.current_node.clients) > 2:
            await self.send(text_data="magic_overload")
        else:
            await self.send(text_data="guest")

    async def disconnect(self, close_code):
        if self.current_node:
            try:
                self.current_node.clients.remove(self)
            except ValueError:
                pass

    async def receive(self, text_data, bytes_data=None):
        if self.current_node:
            for client in self.current_node.clients:
                if client is self:
                    continue
                try:
                    await client.send(text_data=text_data)
                except Exception:
                    pass
