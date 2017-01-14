#!/usr/bin/env python3
"""
Exposes several methods for transmitting cyclic messages.
20/09/13
"""

import can
import abc
import logging
import sched
import threading
import time

log = logging.getLogger('can.bcm')
log.debug("Loading base broadcast manager functionality")


class CyclicSendTaskABC(object):

    def __init__(self, message, period, duration=None):
        """
        :param message: The :class:`can.Message` to be sent periodically.
        :param float period: The rate in seconds at which to send the message.
        """
        self.message = message
        self.period = period
        self.duration = duration

    @abc.abstractmethod
    def stop(self):
        """Cancel this periodic task.
        """


class ModifiableCyclicTaskABC(CyclicSendTaskABC):
    """Adds support for modifying a periodic message"""

    @abc.abstractmethod
    def modify_data(self, message):
        """Update the contents of this periodically sent message without altering
        the timing.

        :param message: The :class:`~can.Message` with new :attr:`Message.data`.
        """


class SimpleCyclicSendManager(object):

    def __init__(self, bus):
        self.bus = bus
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.thread = None

    def add_task(self, task):
        self.schedule_task(task, 0)
        if self.thread is None or not self.thread.is_alive():
            name = "Periodic send thread for " + self.bus.channel_info
            self.thread = threading.Thread(target=self.scheduler.run, name=name)
            self.thread.daemon = True
            self.thread.start()

    def schedule_task(self, task, delay=None):
        self.scheduler.enter(task.period if delay is None else delay,
                             task.message.arbitration_id,
                             self.transmit,
                             (task, ))

    def transmit(self, task):
        if task.stopped or (task.end_time is not None and
                            time.time() > task.end_time):
            return
        self.schedule_task(task)
        self.bus.send(task.message)


class SimpleCyclicSendTask(ModifiableCyclicTaskABC):
    """Fallback cyclic send task using thread."""

    def __init__(self, message, period, duration=None):
        super(SimpleCyclicSendTask, self).__init__(message, period, duration)
        self.stopped = False
        self.end_time = time.time() + duration if duration else None

    def stop(self):
        self.stopped = True

    def modify_data(self, message):
        self.message = message


def send_periodic(channel, message, period):
    """
    Send a message every `period` seconds on the given channel.

    """
    return can.interface.CyclicSendTask(channel, message, period)
