import unittest
from unittest.mock import patch, MagicMock
from xmrig.db import XMRigDatabase
from sqlalchemy.engine import Engine

class TestXMRigDatabase(unittest.TestCase):

    @patch('xmrig.db.create_engine')
    def test_init_db(self, mock_create_engine):
        engine = XMRigDatabase.init_db("sqlite:///test.db")
        self.assertIsInstance(engine, Engine)

    @patch('xmrig.db.pd.DataFrame.to_sql')
    def test_insert_data_to_db(self, mock_to_sql):
        engine = MagicMock()
        XMRigDatabase.insert_data_to_db({"key": "value"}, "test_table", engine)
        mock_to_sql.assert_called_once()

    @patch('xmrig.db.XMRigDatabase.get_data_from_db')
    def test_get_data_from_db(self, mock_get_data_from_db):
        engine = MagicMock()
        mock_get_data_from_db.return_value = {"key": "value"}
        data = XMRigDatabase.get_data_from_db("test_table", ["key"], engine)
        self.assertEqual(data, {"key": "value"})

    @patch('xmrig.db.XMRigDatabase.delete_all_miner_data_from_db')
    def test_delete_all_miner_data_from_db(self, mock_delete_all_miner_data_from_db):
        engine = MagicMock()
        XMRigDatabase.delete_all_miner_data_from_db("test_miner", engine)
        mock_delete_all_miner_data_from_db.assert_called_once()

if __name__ == '__main__':
    unittest.main()
