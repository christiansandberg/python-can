# -*- coding: utf-8 -*-

"""
This module implements an OS and hardware independent
virtual CAN interface for testing purposes.

Any VirtualBus instances connecting to the same channel
will get the same messages.
"""

import logging
import time
try:
    import queue
except ImportError:
    import Queue as queue
from can.bus import BusABC, AsyncMixin


logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)


# Channels are lists of VirtualBuses, one for each connection
channels = {}


class VirtualBus(BusABC, AsyncMixin):
    """Virtual CAN bus using an internal message queue for testing."""

    def __init__(self, channel=None, receive_own_messages=False, **config):
        self.channel_info = 'Virtual bus channel %s' % channel
        self.receive_own_messages = receive_own_messages

        # Create a new channel if one does not exist
        if channel not in channels:
            channels[channel] = []

        self.queue = queue.Queue()
        self.channel = channels[channel]
        self.channel.append(self)

        super(VirtualBus, self).__init__(**config)
        AsyncMixin.__init__(self)

    def recv(self, timeout=None):
        try:
            msg = self.queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

        logger.log(9, 'Received message:\n%s', msg)
        return msg

    def send(self, msg, timeout=None):
        if not msg.timestamp:
            msg.timestamp = time.time()
        # Add message to all listening on this channel
        for bus in self.channel:
            if bus is not self or self.receive_own_messages:
                bus.queue.put(msg)
                bus.message_received()
        logger.log(9, 'Transmitted message:\n%s', msg)

    def shutdown(self):
        self.channel.remove(self.queue)


if __name__ == "__main__":
    from can.message import Message
    bus1 = VirtualBus(0)
    bus2 = VirtualBus(0)

    bus1.on_message(print)
    bus2.send(Message(arbitration_id=0x12345))
