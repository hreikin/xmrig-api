"""
XMRig Database module.

This module provides the XMRigDatabase class for database operations related to the XMRig miner.
It includes functionalities for:

- Initializing the database engine.
- Inserting data into the database.
- Retrieving data from the database.
- Deleting all miner-related data from the database.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from xmrig.helpers import log, XMRigAPIError
from datetime import datetime
from typing import Dict, Any, Union, List
import pandas as pd
import json

# TODO: More refactoring required (probably elsewhere, maybe here as well) to get methods to work with the rest of the codebase

class XMRigDatabase:
    _engines = {}

    @classmethod
    def init_db(cls, db_url: str) -> Engine:
        """
        Initializes the database engine, if it already exists, it returns the existing engine.

        Returns:
            Engine: SQLAlchemy engine instance.
        """
        try:
            if db_url not in cls._engines:
                cls._engines[db_url] = create_engine(db_url)
            return cls._engines[db_url]
        except Exception as e:
            log.error(f"An error occurred initializing the database: {e}")
            raise XMRigAPIError(f"Could not parse SQLAlchemy URL from string '{db_url}'") from e
    
    # TODO: Refactor to only insert the full_json data
    @staticmethod
    def insert_data_to_db(json_data: Dict[str, Any], table_name: str, engine: Engine) -> None:
        """
        Inserts JSON data into the specified database table.

        Args:
            json_data (Dict[str, Any]): JSON data to insert.
            table_name (str): Name of the table to insert data into.
            engine (Engine): SQLAlchemy engine instance.
        """
        try:
            # Create a dataframe with the required columns and data
            data = {
                'timestamp': [datetime.now()],
                'full_json': [json.dumps(json_data)]
            }
            df = pd.DataFrame(data)
            # Insert data into the database
            df.to_sql(table_name, engine, if_exists='append', index=False)
            log.debug("Data inserted successfully")
        except Exception as e:
            log.error(f"An error occurred inserting data to the database: {e}")
            raise XMRigAPIError() from e
    
    # TODO: Refactor to only get the full_json data and then use the json keys to access the correct data
    @staticmethod
    def get_data_from_db(table_name: Union[str, List[str]], keys: List[Union[str, int]], engine: Engine) -> Any:
        """
        Retrieves the data from the database using the provided table name.

        Args:
            table_name (Union[str, List[str]]): The name of the table or list of table names to use to retrieve the data.
            keys (List[Union[str, int]]): The keys to use to retrieve the data.
            engine (Engine): The SQLAlchemy engine instance.
        """
        column_name = "full_json"
        try:
            # connect to the database and fetch the data in column_name from the table_name
            with engine.connect() as connection:
                result = connection.execute(text(f"SELECT {column_name} FROM {table_name} ORDER BY timestamp DESC LIMIT 1"))
                # fetch the last item from the result
                data = result.fetchone()
                if data:
                    data = json.loads(data[0])
                    # use the list of keys/indices to access the correct data
                    if len(keys) > 0:
                        for key in keys:
                            data = data[key]
                    return data
                return "N/A"
        except Exception as e:
            log.error(f"An error occurred retrieving data from the database: {e}")
            raise XMRigAPIError() from e
        return "N/A"

    @staticmethod
    def delete_all_miner_data_from_db(miner_name: str, engine: Engine) -> None:
        """
        Deletes all tables related to a specific miner from the database.

        Args:
            miner_name (str): The unique name of the miner.
            engine (Engine): SQLAlchemy engine instance.
        """
        try:
            # Use quotes to avoid SQL syntax errors
            backends_tables = [f"'{miner_name}-cpu-backend'", f"'{miner_name}-opencl-backend'", f"'{miner_name}-cuda-backend'"]
            config_table = f"'{miner_name}-config'"
            summary_table = f"'{miner_name}-summary'"
            with engine.connect() as connection:
                # Wrap the raw SQL strings in SQLAlchemy's `text` function so it isn't a raw string
                connection.execute(text(f"DROP TABLE IF EXISTS {backends_tables[0]}"))
                connection.execute(text(f"DROP TABLE IF EXISTS {backends_tables[1]}"))
                connection.execute(text(f"DROP TABLE IF EXISTS {backends_tables[2]}"))
                connection.execute(text(f"DROP TABLE IF EXISTS {config_table}"))
                connection.execute(text(f"DROP TABLE IF EXISTS {summary_table}"))
            log.debug(f"All tables for '{miner_name}' have been deleted from the database")
        except Exception as e:
            log.error(f"An error occurred deleting miner '{miner_name}' from the database: {e}")
            raise XMRigAPIError() from e