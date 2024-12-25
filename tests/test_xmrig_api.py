import unittest, json
from unittest.mock import patch, MagicMock
from xmrig.api import XMRigAPI, XMRigAuthorizationError

class TestXMRigAPI(unittest.TestCase):
    """Unit tests for the XMRigAPI class."""

    def setUp(self):
        """Set up the test environment."""
        with patch.object(XMRigAPI, 'get_all_responses', return_value=True):
            self.api = XMRigAPI(miner_name="test_miner", ip="127.0.0.1", port="8080", access_token="fake-token", tls_enabled=False)
        
        with open("api/summary.json", "r") as f:
            self.api._summary_response = json.load(f)
        with open("api/backends.json", "r") as f:
            self.api._backends_response = json.load(f)
        with open("api/config.json", "r") as f:
            self.api._config_response = json.load(f)

    @patch("requests.get")
    def test_get_summary_success(self, mock_get):
        """Test successful retrieval of summary."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}
        mock_get.return_value = mock_response

        result = self.api.get_summary()

        self.assertTrue(result)
        self.assertEqual(self.api._summary_response, {"key": "value"})

    @patch("requests.get")
    def test_get_summary_auth_error(self, mock_get):
        """Test authorization error when retrieving summary."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_get.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.get_summary()

    @patch("requests.get")
    def test_get_backends_success(self, mock_get):
        """Test successful retrieval of backends."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"backend_key": "backend_value"}
        mock_get.return_value = mock_response

        result = self.api.get_backends()

        self.assertTrue(result)
        self.assertEqual(self.api._backends_response, {"backend_key": "backend_value"})

    @patch("requests.get")
    def test_get_backends_auth_error(self, mock_get):
        """Test authorization error when retrieving backends."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_get.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.get_backends()

    @patch("requests.get")
    def test_get_config_success(self, mock_get):
        """Test successful retrieval of config."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"config_key": "config_value"}
        mock_get.return_value = mock_response

        result = self.api.get_config()

        self.assertTrue(result)
        self.assertEqual(self.api._config_response, {"config_key": "config_value"})

    @patch("requests.get")
    def test_get_config_auth_error(self, mock_get):
        """Test authorization error when retrieving config."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_get.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.get_config()

    @patch("requests.post")
    def test_post_config_success(self, mock_post):
        """Test successful posting of config."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.post_config({"new_config_key": "new_config_value"})

        self.assertTrue(result)

    @patch("requests.post")
    def test_post_config_auth_error(self, mock_post):
        """Test authorization error when posting config."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Unauthorized"}
        mock_post.return_value = mock_response

        with self.assertRaises(XMRigAuthorizationError):
            self.api.post_config({"new_config_key": "new_config_value"})

    @patch("requests.post")
    def test_pause_miner_success(self, mock_post):
        """Test successful pausing of miner."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.pause_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_resume_miner_success(self, mock_post):
        """Test successful resuming of miner."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.resume_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_stop_miner_success(self, mock_post):
        """Test successful stopping of miner."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.stop_miner()

        self.assertTrue(result)

    @patch("requests.post")
    def test_start_miner_success(self, mock_post):
        """Test successful starting of miner."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        result = self.api.start_miner()

        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()