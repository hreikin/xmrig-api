import unittest
from unittest.mock import patch, MagicMock
from xmrig.manager import XMRigManager
from xmrig.api import XMRigAPI

class TestXMRigManager(unittest.TestCase):

    def setUp(self):
        self.manager = XMRigManager()

    @patch('xmrig.manager.requests.get')
    @patch('xmrig.manager.XMRigAPI.get_endpoint', return_value=True)
    @patch('xmrig.manager.XMRigAPI.get_all_responses', return_value=True)
    @patch('xmrig.manager.XMRigAPI')
    def test_add_miner(self, mock_api, mock_get_all_responses, mock_get_endpoint, mock_requests_get):
        mock_requests_get.return_value.status_code = 200
        mock_requests_get.return_value.json.return_value = {}
        self.manager.add_miner("test_miner", "127.0.0.1", 8080)
        self.assertIn("test_miner", self.manager._miners)

    @patch('xmrig.manager.XMRigDatabase.delete_all_miner_data_from_db')
    def test_remove_miner(self, mock_delete_all_miner_data_from_db):
        self.manager._miners["test_miner"] = MagicMock()
        self.manager.remove_miner("test_miner")
        self.assertNotIn("test_miner", self.manager._miners)
        mock_delete_all_miner_data_from_db.assert_called_once()

    def test_get_miner(self):
        self.manager._miners["test_miner"] = MagicMock()
        miner = self.manager.get_miner("test_miner")
        self.assertIsNotNone(miner)

    @patch('xmrig.manager.XMRigAPI.get_all_responses')
    def test_update_miners(self, mock_get_all_responses):
        self.manager._miners["test_miner"] = MagicMock()
        mock_get_all_responses.return_value = True
        self.assertTrue(self.manager.update_miners())

    def test_list_miners(self):
        self.manager._miners["test_miner"] = MagicMock()
        self.assertIn("test_miner", self.manager.list_miners())

if __name__ == '__main__':
    unittest.main()
