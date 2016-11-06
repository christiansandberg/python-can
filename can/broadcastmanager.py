#!/usr/bin/env python3
"""
Exposes several methods for transmitting cyclic messages.
20/09/13
"""

import can
import abc
import logging
import threading
import time

log = logging.getLogger('can.bcm')
log.debug("Loading base broadcast manager functionality")


class CyclicTask(object):

    def stop(self):
        """Cancel the periodic task"""
        raise NotImplementedError()

    def start(self):
        """Once stopped a task can be restarted"""
        raise NotImplementedError()


class CyclicSendTaskABC(CyclicTask):

    def __init__(self, channel, message, period):
        """
        :param str channel: The name of the CAN channel to connect to.
        :param message: The :class:`can.Message` to be sent periodically.
        :param float period: The rate in seconds at which to send the message.
        """
        self.can_id = message.arbitration_id
        self.period = period

    @abc.abstractmethod
    def stop(self):
        """Send a TX_DELETE message to the broadcast manager to cancel this task.

        This will delete the entry for the transmission of the CAN message
        specified.
        """

    @abc.abstractmethod
    def modify_data(self, message):
        """Update the contents of this periodically sent message without altering
        the timing.

        :param message: The :class:`~can.Message` with new :attr:`Message.data`.
            Note it must have the same :attr:`~can.Message.arbitration_id`.
        """


class MultiRateCyclicSendTaskABC(CyclicSendTaskABC):

    """Exposes more of the full power of the TX_SETUP opcode.

    Transmits a message `count` times at `initial_period` then
    continues to transmit message at `subsequent_period`.
    """

    def __init__(self, channel, message, count, initial_period, subsequent_period):
        super(MultiRateCyclicSendTaskABC, self).__init__(channel, message, subsequent_period)


class SimpleCyclicSendTask(CyclicSendTaskABC):
    """Fallback cyclic send task using thread."""

    def __init__(self, channel, message, period, **config):
        self.channel = channel
        self.message = message
        self.period = period
        self.config = config
        super(SimpleCyclicSendTask, self).__init__(None, message, period)

        self.start()

    def _bus_setup(self):
        self.bus = can.interface.Bus(self.channel, **self.config)

    def start(self):
        self._bus_setup()

        self.running = threading.Event()
        self.running.set()

        self._sender = threading.Thread(target=self.tx_thread)
        self._sender.daemon = True

        self._sender.start()

    def stop(self):
        self.running.clear()
        self._sender.join(5)
        self.bus.shutdown()

    def tx_thread(self):
        while self.running.is_set():
            self.bus.send(self.message)
            time.sleep(self.period)

    def modify_data(self, message):
        self.message = message


def send_periodic(channel, message, period):
    """
    Send a message every `period` seconds on the given channel.

    """
    return can.interface.CyclicSendTask(channel, message, period)
