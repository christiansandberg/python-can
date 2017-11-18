"""Module for asyncio support."""
try:
    import asyncio
except ImportError:
    asyncio = None
from .listener import Listener


class AsyncMixin(object):
    """Can be used to add support for asyncio in a Bus class.

    The bus should implement :meth:`._start_callbacks` and possibly
    :meth:`._stop_callbacks`. When a message has been received, :meth:`._notify`
    should be called from the main thread or :meth:`._notify_threadsafe` if it
    is called from another thread.
    """

    def __init__(self, loop=None, *args, **kwargs):
        if loop is None and asyncio is not None:
            try:
                loop = asyncio.get_event_loop()
            except:
                # Probably in a thread
                pass
        self._loop = loop
        self._callbacks = []

    def add_callback(self, cb):
        """Add a callback or a :class:`can.Listener` instance to be called when
        a message is received.

        :param cb: Callable function or Listener instance.
        """
        if asyncio is None:
            raise RuntimeError("Asynchronous operation requires Python 3.4")
        self._callbacks.append(cb)
        if len(self._callbacks) == 1:
            # First callback registered
            self._start_callbacks()

    def remove_callback(self, cb):
        """Remove callback.

        :param cb: Callable function or Listener instance.
        """
        self._callbacks = [fn for fn in self._callbacks if fn != cb]
        if not self._callbacks:
            self._stop_callbacks()

    def _start_callbacks(self):
        """Starts the process of calling :meth:`notify`."""
        pass

    def _stop_callbacks(self):
        """Stop calling notify."""
        pass

    def _notify(self):
        """Called when a new message exists.
        
        Must be called from the same thread as the event loop.
        """
        while True:
            msg = self.recv(0)
            if msg is None:
                break
            self._invoke_callbacks(msg)

    def _notify_threadsafe(self, *args, **kwargs):
        """Called from a different thread when a new message exists."""
        self._loop.call_soon_threadsafe(self._notify)

    def _invoke_callbacks(self, msg):
        for callback in self._callbacks:
            res = callback(msg)
            if asyncio.iscoroutine(res):
                self._loop.create_task(res)


class AsyncListener(Listener, AsyncMixin):
    """Feeds messages to an asyncio application."""

    def on_message_received(self, msg):
        self._loop.call_soon_threadsafe(self._invoke_callbacks, msg)

