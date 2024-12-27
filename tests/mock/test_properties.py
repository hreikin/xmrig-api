import unittest
from unittest.mock import patch, MagicMock
from xmrig.properties import XMRigProperties

class TestXMRigProperties(unittest.TestCase):

    def setUp(self):
        self.summary_response = {"id": "test_id", "worker_id": "test_worker_id", "uptime": 3600, "restricted": False, "resources": {"memory": {"free": 1024, "total": 2048}}}
        self.backends_response = [{"type": "cpu", "enabled": True, "algo": "rx/0"}]
        self.config_response = {"algo": "rx/0"}
        self.miner_name = "test_miner"
        self.db_url = "sqlite:///test.db"
        self.properties = XMRigProperties(self.summary_response, self.backends_response, self.config_response, self.miner_name, self.db_url)

    def test_summary(self):
        self.assertEqual(self.properties.summary, self.summary_response)

    def test_sum_id(self):
        self.assertEqual(self.properties.sum_id, "test_id")

    def test_sum_worker_id(self):
        self.assertEqual(self.properties.sum_worker_id, "test_worker_id")

    def test_sum_uptime(self):
        self.assertEqual(self.properties.sum_uptime, 3600)

    def test_sum_uptime_readable(self):
        self.assertEqual(self.properties.sum_uptime_readable, "1:00:00")

    def test_sum_restricted(self):
        self.assertEqual(self.properties.sum_restricted, False)

    def test_sum_free_memory(self):
        self.assertEqual(self.properties.sum_free_memory, 1024)

    def test_sum_total_memory(self):
        self.assertEqual(self.properties.sum_total_memory, 2048)

    @patch('xmrig.properties.XMRigDatabase.fallback_to_db')
    def test_fallback_to_db(self, mock_fallback_to_db):
        mock_fallback_to_db.return_value = "db_value"
        self.properties._db_engine = MagicMock()
        self.assertEqual(self.properties._get_data_from_response({}, ["key"], "table"), "db_value")

if __name__ == '__main__':
    unittest.main()
