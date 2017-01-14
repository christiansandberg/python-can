from time import sleep
import unittest
import logging
import can

logging.getLogger(__file__).setLevel(logging.DEBUG)


class SimpleCyclicSendTaskTest(unittest.TestCase):

    def test_cycle_time(self):
        msg = can.Message(extended_id=False, arbitration_id=0x100, data=[0,1,2,3,4,5,6,7])
        bus = can.interface.Bus(bustype='virtual')
        task = bus.send_periodic(msg, 0.01, 1)
        sleep(1.5)
        size = bus.queue.qsize()
        period = 1.0 / size
        print('Actual period = %f s' % period)
        self.assertTrue(0.008 <= period <= 0.013)
        last_msg = bus.recv()
        self.assertEqual(last_msg.arbitration_id, 0x100)


if __name__ == '__main__':
    unittest.main()
