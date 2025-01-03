import unittest
from unittest.mock import patch, MagicMock
from xmrig.api import XMRigAPI

class TestXMRigAPI(unittest.TestCase):

    @patch('xmrig.api.XMRigAPI.get_all_responses', return_value=True)
    def setUp(self, mock_get_all_responses):
        self.api = XMRigAPI("test_miner", "127.0.0.1", "8080")

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_summary(self, mock_get):
        mock_get.return_value.json.return_value = {"id": "test_id"}
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("summary"))

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_backends(self, mock_get):
        mock_get.return_value.json.return_value = [{"type": "cpu"}]
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("backends"))

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_config(self, mock_get):
        mock_get.return_value.json.return_value = {"algo": "rx/0"}
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("config"))

    @patch('xmrig.api.requests.post')
    @patch('xmrig.api.XMRigAPI.get_endpoint', return_value=True)
    def test_post_config(self, mock_get_endpoint, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.post_config({"algo": "rx/0"}))

    @patch('xmrig.api.requests.post')
    def test_perform_action_pause(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.perform_action("pause"))

    @patch('xmrig.api.requests.post')
    def test_perform_action_resume(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.perform_action("resume"))

    @patch('xmrig.api.requests.post')
    def test_perform_action_stop(self, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.perform_action("stop"))

    @patch('xmrig.api.requests.post')
    @patch('xmrig.api.XMRigAPI.get_endpoint', return_value=True)
    def test_perform_action_start(self, mock_get_endpoint, mock_post):
        mock_post.return_value.status_code = 200
        self.assertTrue(self.api.perform_action("start"))

if __name__ == '__main__':
    unittest.main()
