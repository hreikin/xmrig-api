import unittest
from unittest.mock import patch, MagicMock
from xmrig.manager import XMRigManager
from xmrig.api import XMRigAPI

class TestXMRigManager(unittest.TestCase):

    def setUp(self):
        self.manager = XMRigManager()

    @patch('xmrig.manager.XMRigAPI')
    def test_add_miner(self, mock_api):
        self.manager.add_miner("test_miner", "127.0.0.1", 8080)
        self.assertIn("test_miner", self.manager._miners)

    def test_remove_miner(self):
        self.manager._miners["test_miner"] = MagicMock()
        self.manager.remove_miner("test_miner")
        self.assertNotIn("test_miner", self.manager._miners)

    def test_get_miner(self):
        self.manager._miners["test_miner"] = MagicMock()
        miner = self.manager.get_miner("test_miner")
        self.assertIsNotNone(miner)

    @patch('xmrig.manager.XMRigAPI.get_all_responses')
    def test_get_all_miners_endpoints(self, mock_get_all_responses):
        self.manager._miners["test_miner"] = MagicMock()
        mock_get_all_responses.return_value = True
        self.assertTrue(self.manager.get_all_miners_endpoints())

    def test_list_miners(self):
        self.manager._miners["test_miner"] = MagicMock()
        self.assertIn("test_miner", self.manager.list_miners())

if __name__ == '__main__':
    unittest.main()
