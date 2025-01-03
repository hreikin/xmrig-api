import unittest
from unittest.mock import patch, MagicMock
from xmrig.db import XMRigDatabase
from sqlalchemy.engine import Engine

class TestXMRigDatabase(unittest.TestCase):

    @patch('xmrig.db.create_engine')
    def test_init_db(self, mock_create_engine):
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        engine = XMRigDatabase.init_db("sqlite:///test.db")
        self.assertIsInstance(engine, Engine)

    @patch('xmrig.db.pd.DataFrame.to_sql')
    @patch('xmrig.db.XMRigDatabase.get_db')
    def test_insert_data_to_db(self, mock_get_db, mock_to_sql):
        mock_get_db.return_value = MagicMock()
        XMRigDatabase.insert_data_to_db({"key": "value"}, "test_table", "sqlite:///test.db")
        mock_to_sql.assert_called_once()

    @patch('xmrig.db.XMRigDatabase.get_db')
    @patch('xmrig.db.inspect')
    def test_check_table_exists(self, mock_inspect, mock_get_db):
        mock_engine = MagicMock()
        mock_get_db.return_value = mock_engine
        mock_inspect.return_value.get_table_names.return_value = ["test_table"]
        exists = XMRigDatabase.check_table_exists("sqlite:///test.db", "'test_table'")
        self.assertTrue(exists)

    @patch('xmrig.db.XMRigDatabase.get_db')
    @patch('xmrig.db.text')
    def test_fallback_to_db(self, mock_text, mock_get_db):
        mock_engine = MagicMock()
        mock_get_db.return_value = mock_engine
        mock_connection = mock_engine.connect.return_value.__enter__.return_value
        mock_connection.execute.return_value.fetchone.return_value = ('{"key": "value"}',)
        data = XMRigDatabase.fallback_to_db("test_table", ["key"], "sqlite:///test.db")
        self.assertEqual(data, "value")

    @patch('xmrig.db.XMRigDatabase.get_db')
    @patch('xmrig.db.text')
    def test_delete_all_miner_data_from_db(self, mock_text, mock_get_db):
        mock_engine = MagicMock()
        mock_get_db.return_value = mock_engine
        XMRigDatabase.delete_all_miner_data_from_db("test_miner", "sqlite:///test.db")
        self.assertTrue(mock_text.called)

if __name__ == '__main__':
    unittest.main()
