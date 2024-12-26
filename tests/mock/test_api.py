import unittest
from unittest.mock import patch, MagicMock
from xmrig.api import XMRigAPI

class TestXMRigAPI(unittest.TestCase):

    def setUp(self):
        self.api = XMRigAPI("test_miner", "127.0.0.1", 8080)

    @patch('xmrig.api.requests.get')
    def test_get_summary(self, mock_get):
        mock_get.return_value.json.return_value = {"id": "test_id"}
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_summary())

    @patch('xmrig.api.requests.get')
    def test_get_backends(self, mock_get):
        mock_get.return_value.json.return_value = [{"type": "cpu"}]
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_backends())

    @patch('xmrig.api.requests.get')
    def test_get_config(self, mock_get):
        mock_get.return_value.json.return_value = {"algo": "rx/0"}
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_config())

    @patch('xmrig.api.requests.post')
    def test_post_config(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.post_config({"algo": "rx/0"}))

    @patch('xmrig.api.requests.post')
    def test_pause_miner(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.pause_miner())

    @patch('xmrig.api.requests.post')
    def test_resume_miner(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.resume_miner())

    @patch('xmrig.api.requests.post')
    def test_stop_miner(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.stop_miner())

    @patch('xmrig.api.requests.post')
    def test_start_miner(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.start_miner())

if __name__ == '__main__':
    unittest.main()
