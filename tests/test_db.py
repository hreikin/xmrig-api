import unittest
from unittest.mock import patch, MagicMock
from xmrig.db import XMRigDatabase
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

class TestXMRigDatabase(unittest.TestCase):

    @patch('xmrig.db.create_engine')
    def test_init_db(self, mock_create_engine):
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        engine = XMRigDatabase.init_db("sqlite:///test.db")
        self.assertIsInstance(engine, Engine)

    @patch('xmrig.db.XMRigDatabase.get_db_session')
    def test_insert_data_to_db_summary(self, mock_get_db_session):
        mock_session = MagicMock(spec=Session)
        mock_get_db_session.return_value = mock_session
        json_data = {
            "id": "test_id",
            "worker_id": "test_worker",
            "uptime": 1000,
            "restricted": False,
            "resources": {
                "memory": {
                    "free": 1000,
                    "total": 2000,
                    "resident_set_memory": 500
                },
                "load_average": [0.1, 0.2, 0.3],
                "hardware_concurrency": 4
            },
            "results": {
                "diff_current": 100,
                "shares_good": 10,
                "shares_total": 20,
                "avg_time": 30,
                "avg_time_ms": 30000,
                "hashes_total": 100000,
                "best": {"hash": "best_hash"}
            },
            "algo": "test_algo",
            "connection": {
                "ip": "127.0.0.1",
                "uptime": 1000,
                "uptime_ms": 1000000,
                "ping": 10,
                "failures": 0,
                "tls": True,
                "tls-fingerprint": "test_fingerprint",
                "algo": "test_algo",
                "diff": 100,
                "accepted": 10,
                "rejected": 0,
                "avg_time": 30,
                "avg_time_ms": 30000,
                "hashes_total": 100000
            },
            "version": "test_version",
            "kind": "test_kind",
            "ua": "test_ua",
            "cpu": {
                "brand": "test_brand",
                "family": 6,
                "model": 158,
                "stepping": 10,
                "proc_info": 0,
                "aes": True,
                "avx2": True,
                "x64": True,
                "64_bit": True,
                "l2": 256,
                "l3": 8192,
                "cores": 4,
                "threads": 8,
                "packages": 1,
                "nodes": 1,
                "backend": "test_backend",
                "msr": "test_msr",
                "assembly": "test_assembly",
                "arch": "test_arch",
                "flags": ["flag1", "flag2"]
            },
            "donate_level": 1,
            "paused": False,
            "algorithms": ["algo1", "algo2"],
            "hashrate": {
                "total": 1000,
                "highest": 1200.5
            },
            "hugepages": {"enabled": True}
        }
        XMRigDatabase.insert_data_to_db(json_data, "test_miner", "summary", "sqlite:///test.db")
        self.assertTrue(mock_session.add.called)
        self.assertTrue(mock_session.commit.called)

    @patch('xmrig.db.XMRigDatabase.get_db_session')
    def test_retrieve_data_from_db(self, mock_get_db_session):
        mock_session = MagicMock(spec=Session)
        mock_get_db_session.return_value = mock_session
        mock_query = mock_session.query.return_value
        mock_query.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [MagicMock(_asdict=lambda: {"key": "value"})]
        data = XMRigDatabase.retrieve_data_from_db("sqlite:///test.db", "summary", "test_miner")
        self.assertEqual(data, [{"key": "value"}])

    @patch('xmrig.db.XMRigDatabase.get_db_session')
    def test_delete_all_miner_data_from_db(self, mock_get_db_session):
        mock_session = MagicMock(spec=Session)
        mock_get_db_session.return_value = mock_session
        XMRigDatabase.delete_all_miner_data_from_db("test_miner", "sqlite:///test.db")
        self.assertTrue(mock_session.query.return_value.filter.return_value.delete.called)
        self.assertTrue(mock_session.commit.called)

if __name__ == '__main__':
    unittest.main()
