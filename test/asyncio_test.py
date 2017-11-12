import unittest

import can

INTERFACE = 'virtual'
CHANNEL = 'vcan0'


class AsyncTest(unittest.TestCase):

    def test_callback(self):
        bus1 = can.interface.Bus(bustype=INTERFACE, channel=CHANNEL)
        bus2 = can.interface.Bus(bustype=INTERFACE, channel=CHANNEL)
        listener = can.BufferedReader()

        bus1.add_callback(listener)
        bus1.add_callback(print)

        msg1 = can.Message(arbitration_id=0x123, extended_id=False)
        msg2 = can.Message(arbitration_id=0x45678, extended_id=True)
        bus2.send(msg1)
        bus2.send(msg2)

        self.assertEqual(listener.get_message(), msg1)
        self.assertEqual(listener.get_message(), msg2)

        bus1.remove_callback(listener)
        bus2.send(msg1)
        # No message should be sent to listener
        self.assertEqual(len(listener), 0)

        bus1.shutdown()
        bus2.shutdown()


if __name__ == "__main__":
    unittest.main()
