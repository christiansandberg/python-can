Asynchronous operation
======================

The library can be used as part of an asyncio_ application.
This means that threads are not needed to asynchronously receive messages.

Currently this is supported by the following interfaces:

* SocketCAN
* Kvaser
* Remote
* Virtual


Usage
-----

You can add callbacks.


API
---

.. autoclass:: can.async.AsyncMixin
   :private-members:


.. _asyncio: https://docs.python.org/3/library/asyncio.html

