from time import sleep
import unittest
import logging
import can

logging.getLogger(__file__).setLevel(logging.DEBUG)


class SimpleCyclicSendTaskTest(unittest.TestCase):

    def test_cycle_time(self):
        msg = can.Message(extended_id=False, arbitration_id=0x100, data=[0,1,2,3,4,5,6,7])
        task = can.interface.CyclicSendTask(0, msg, 0.02, bustype='virtual')
        sleep(1.0)
        size = task.bus.queue.qsize()
        period = 1.0 / size
        print('Actual period = %f s' % period)
        self.assertTrue(0.015 <= period <= 0.025)

        task.stop()
        sleep(0.5)
        self.assertEqual(task.bus.queue.qsize(), size)

        last_msg = task.bus.recv()
        self.assertEqual(last_msg.arbitration_id, 0x100)


if __name__ == '__main__':
    unittest.main()
