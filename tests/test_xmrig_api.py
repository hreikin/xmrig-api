import unittest
from unittest.mock import patch, MagicMock
from xmrig.api import XMRigAPI, XMRigAuthorizationError


class TestXMRigAPI(unittest.TestCase):

    def setUp(self):
        with patch.object(XMRigAPI, 'update_all_responses', return_value=True):
            self.api = XMRigAPI(ip="127.0.0.1", port="8080", access_token="fake-token", tls_enabled=False)

    @patch("requests.get")
    def test_update_summary_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = self.api.update_summary()

        self.assertTrue(result)
        self.assertEqual(self.api._summary_response, {"key": "value"})

    @patch("requests.get")
    def test_update_summary_auth_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.update_summary()

    @patch("requests.get")
    def test_update_backends_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"backend_key": "backend_value"}
        mock_get.return_value = mock_response

        result = self.api.update_backends()

        self.assertTrue(result)
        self.assertEqual(self.api._backends_response, {"backend_key": "backend_value"})

    @patch("requests.get")
    def test_update_config_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"config_key": "config_value"}
        mock_get.return_value = mock_response

        result = self.api.update_config()

        self.assertTrue(result)
        self.assertEqual(self.api._config_response, {"config_key": "config_value"})

    @patch("requests.post")
    def test_post_config_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.post_config({"new_config_key": "new_config_value"})

        self.assertTrue(result)

    @patch("requests.post")
    def test_pause_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.pause_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_resume_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.resume_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_stop_miner_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.stop_miner()

        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()