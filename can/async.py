try:
    import asyncio
except ImportError:
    asyncio = None


class AsyncMixin(object):

    def __init__(self, loop=None):
        if loop is None and asyncio is not None:
            try:
                loop = asyncio.get_event_loop()
            except:
                # Probably in a thread
                pass
        self._loop = loop
        self._callbacks = []

    def on_message(self, cb):
        if asyncio is None:
            raise RuntimeError("Asynchronous operation requires Python 3.4")
        self._callbacks.append(cb)
        if len(self._callbacks) == 1:
            # First callback registered
            self.start_callbacks()

    def start_callbacks(self):
        pass

    def stop_callbacks(self):
        pass

    def notify(self):
        while True:
            msg = self.recv(0)
            if msg is None:
                break
            for callback in self._callbacks:
                res = callback(msg)
                if asyncio.iscoroutine(res):
                    self._loop.create_task(res)
