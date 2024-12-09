import unittest, json
from xmrig_api import XMRigAPI

class TestConfigProperties(unittest.TestCase):
    """
    Tests that ensure the properties relating to the summary endpoint return the expected value. 
    These tests require a running instance of XMRig to be configured but are run against cached 
    data.
    """
    def setUp(self):
        """
        Instantiate the XMRig API client and feed it cached data to run the tests with.
        """
        self.api = XMRigAPI(ip="127.0.0.1", port="37841", access_token="SECRET")

        ##### Comment this block out to run against live data.
        with open("example-api/example-config.json", "r") as f:
            self.mock_config = json.load(f)
        self.api._config_response = self.mock_config
        #####

    def test_config_property(self):
        """Test that the 'config' property returns a dictionary containing an 'api' key."""
        result = self.api.config
        self.assertIsInstance(result, dict)
        self.assertIn("api", result)


if __name__ == "__main__":
    unittest.main()
