import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.engine import Engine
from xmrig.db import XMRigDatabase
from xmrig.api import XMRigAPI

class TestXmrigDb(unittest.TestCase):
    """Unit tests for the XMRigDatabase class."""
    def setUp(self):
        # TODO: Create tests for properties in the scenario where the JSON response data is 
        # TODO: not available and the database is queried instead, will require a cached db,
        # TODO: use similar tests to the ones within TestXMRigProperties class in 
        # TODO: test_xmrig_properties.py which need dixing first
        """Set up the test environment by initializing the database from a saved file."""
        self.db_url = 'sqlite:///api/xmrig-db.db'
        self.engine = XMRigDatabase.init_db(self.db_url)
        with patch.object(XMRigAPI, 'get_all_responses', return_value=True):
            self.api = XMRigAPI(miner_name="test_miner", ip="127.0.0.1", port="8080", access_token="fake-token", tls_enabled=False)
        self.api._summary_response = None
        self.api._backends_response = None
        self.api._config_response = None
        self.api._update_properties_cache()

    @patch('xmrig.db.create_engine')
    def test_init_db(self, mock_create_engine):
        """Test initializing the database engine."""
        db_url = 'sqlite:///test.db'
        mock_engine = MagicMock(spec=Engine)
        mock_create_engine.return_value = mock_engine

        engine = XMRigDatabase.init_db(db_url)
        mock_create_engine.assert_called_once_with(db_url)
        self.assertEqual(engine, mock_engine)

    @patch('xmrig.db.pd.DataFrame.to_sql')
    def test_insert_data_to_db(self, mock_to_sql):
        """Test inserting data into the database."""
        json_data = {'key': 'value'}
        table_name = 'test_table'
        mock_engine = MagicMock(spec=Engine)

        XMRigDatabase.insert_data_to_db(json_data, table_name, mock_engine)
        mock_to_sql.assert_called_once()

    @patch('xmrig.db.XMRigDatabase.get_data_from_db')
    def test_get_data_from_db(self, mock_get_data_from_db):
        """Test retrieving data from the database."""
        table_name = 'test_table'
        keys = ['key']
        mock_engine = MagicMock(spec=Engine)
        expected_data = 'value'
        mock_get_data_from_db.return_value = expected_data

        data = XMRigDatabase.get_data_from_db(table_name, keys, mock_engine)
        mock_get_data_from_db.assert_called_once_with(table_name, keys, mock_engine)
        self.assertEqual(data, expected_data)

    @patch('xmrig.db.XMRigDatabase.delete_all_miner_data_from_db')
    def test_delete_all_miner_data_from_db(self, mock_delete_all_miner_data_from_db):
        """Test deleting all miner-related data from the database."""
        miner_name = 'test_miner'
        mock_engine = MagicMock(spec=Engine)

        XMRigDatabase.delete_all_miner_data_from_db(miner_name, mock_engine)
        mock_delete_all_miner_data_from_db.assert_called_once_with(miner_name, mock_engine)

if __name__ == "__main__":
    unittest.main()