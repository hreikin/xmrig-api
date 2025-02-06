import unittest, json
from unittest.mock import patch
from xmrig.api import XMRigAPI

class TestXMRigAPI(unittest.TestCase):

    @patch('xmrig.api.XMRigAPI.get_all_responses', return_value=True)
    def setUp(self, mock_get_all_responses):
        with open("api/summary.json", "r") as f:
            self.summary = json.loads(f.read())
        with open("api/backends.json", "r") as f:
            self.backends = json.loads(f.read())
        with open("api/config.json", "r") as f:
            self.config = json.loads(f.read())
        self.api = XMRigAPI("test_miner", "127.0.0.1", "8080")
        self.api._update_cache(self.summary, "summary")
        self.api._update_cache(self.backends, "backends")
        self.api._update_cache(self.config, "config")

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_summary(self, mock_get):
        mock_get.return_value.json.return_value = self.summary
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("summary"))

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_backends(self, mock_get):
        mock_get.return_value.json.return_value = self.backends
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("backends"))

    @patch('xmrig.api.requests.get')
    def test_get_endpoint_config(self, mock_get):
        mock_get.return_value.json.return_value = self.config
        mock_get.return_value.status_code = 200
        self.assertTrue(self.api.get_endpoint("config"))

    @patch('xmrig.api.requests.post')
    @patch('xmrig.api.XMRigAPI.get_endpoint', return_value=True)
    def test_post_config(self, mock_get_endpoint, mock_post):
        mock_post.return_value.status_code = 200
        test_config = self.config
        test_config["api"]["id"] = "test_miner"
        self.assertTrue(self.api.post_config(test_config))

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
