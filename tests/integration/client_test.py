import unittest
from types import StringTypes

from dce import DCEAPIClient
from dce.consts import DCE_MODES
from dce.errors import InvalidVersion
from ..envs import *


class ClientTest(unittest.TestCase):
    api26 = DCEAPIClient(DCE_HOST_2_6, username=DCE_USERNAME, password=DCE_PASSWORD)
    api28 = DCEAPIClient(DCE_HOST_2_8, username=DCE_USERNAME, password=DCE_PASSWORD)

    def test_min_version(self):
        with self.assertRaises(InvalidVersion):
            DCEAPIClient(DCE_HOST, username=DCE_USERNAME, password=DCE_PASSWORD, min_version='100.0.0')

    def test_ping(self):
        self.assertEqual(self.api26.ping(), 'OK')
        self.assertEqual(self.api28.ping(), 'OK')

    def test_now(self):
        self.assertIsInstance(self.api26.now(), float)
        self.assertIsInstance(self.api28.now(), float)

    def test_info(self):
        self.assertIsInstance(self.api26.cluster_uuid, StringTypes)
        self.assertIsInstance(self.api28.cluster_uuid, StringTypes)
        self.assertIsInstance(self.api26.virt_tech, StringTypes)
        self.assertIsInstance(self.api28.virt_tech, StringTypes)
        self.assertIsInstance(self.api26.virt_tech_type, StringTypes)
        self.assertIsInstance(self.api28.virt_tech_type, StringTypes)
        self.assertIsInstance(self.api26.stream_room, StringTypes)
        self.assertIsInstance(self.api28.stream_room, StringTypes)

        self.assertIn(self.api28.mode, DCE_MODES)
        with self.assertRaises(InvalidVersion):
            print(self.api26.mode)
        self.assertIn(self.api28.network_driver, ('calico', 'flannel'))
        with self.assertRaises(InvalidVersion):
            print(self.api26.network_driver)
