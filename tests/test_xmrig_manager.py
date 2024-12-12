import unittest
from unittest.mock import MagicMock, patch
from xmrig import XMRigManager, XMRigAPI

class TestXMRigManager(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment, including a mock XMRigManager instance and mocked miners.
        """
        # Create a mocked factory and mock miner instances
        self.mock_api_factory = MagicMock()
        self.mock_miner_1 = MagicMock()
        self.mock_miner_2 = MagicMock()

        # Mock the factory to return specific mock miners
        self.mock_api_factory.side_effect = [self.mock_miner_1, self.mock_miner_2]

        # Inject the mocked factory into the manager
        self.manager = XMRigManager(api_factory=self.mock_api_factory)

    def test_add_miner(self):
        """Test adding a miner to the manager."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080", "token1", tls_enabled=False)
        self.manager.add_miner("Miner2", "192.168.0.102", "8081", "token2", tls_enabled=True)

        self.assertIn("Miner1", self.manager.list_miners())
        self.assertIn("Miner2", self.manager.list_miners())

    def test_add_duplicate_miner(self):
        """Test that adding a miner with a duplicate name raises an error."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        with self.assertRaises(ValueError):
            self.manager.add_miner("Miner1", "192.168.0.102", "8081")

    def test_remove_miner(self):
        """Test removing a miner from the manager."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        self.manager.remove_miner("Miner1")

        self.assertNotIn("Miner1", self.manager.list_miners())

    def test_remove_nonexistent_miner(self):
        """Test that removing a nonexistent miner raises an error."""
        with self.assertRaises(ValueError):
            self.manager.remove_miner("NonExistentMiner")

    def test_get_miner(self):
        """Test retrieving a specific miner's API instance."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        miner = self.manager.get_miner("Miner1")

        # Use mock comparison
        self.assertIs(miner, self.mock_miner_1)

    def test_get_nonexistent_miner(self):
        """Test that retrieving a nonexistent miner raises an error."""
        with self.assertRaises(ValueError):
            self.manager.get_miner("NonExistentMiner")

    def test_perform_action_on_all(self):
        """Test performing an action on all miners."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        self.manager.add_miner("Miner2", "192.168.0.102", "8081")

        # Mock methods for the miners
        self.mock_miner_1.pause_miner.return_value = True
        self.mock_miner_2.pause_miner.return_value = True

        self.manager.perform_action_on_all("pause")

        # Verify calls
        self.mock_miner_1.pause_miner.assert_called_once()
        self.mock_miner_2.pause_miner.assert_called_once()

    def test_update_all_miners(self):
        """Test updating cached data for all miners."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        self.manager.add_miner("Miner2", "192.168.0.102", "8081")

        # Mock methods for the miners
        self.mock_miner_1.update_all_responses.return_value = True
        self.mock_miner_2.update_all_responses.return_value = True

        self.manager.update_all_miners()

        # Verify calls
        self.mock_miner_1.update_all_responses.assert_called_once()
        self.mock_miner_2.update_all_responses.assert_called_once()

    def test_list_miners(self):
        """Test listing all managed miners."""
        self.manager.add_miner("Miner1", "192.168.0.101", "8080")
        self.manager.add_miner("Miner2", "192.168.0.102", "8081")

        miners = self.manager.list_miners()
        self.assertIn("Miner1", miners)
        self.assertIn("Miner2", miners)

if __name__ == '__main__':
    unittest.main()
