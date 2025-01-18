"""
XMRig Database module.

This module provides the XMRigDatabase class for database operations related to the XMRig miner.
It includes functionalities for:

- Initializing the database engine.
- Inserting data into the database.
- Retrieving data from the database.
- Deleting all miner-related data from the database.
"""

from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from xmrig.logger import log
from xmrig.exceptions import XMRigDatabaseError
from datetime import datetime
from typing import Dict, Any, Union, List
import pandas as pd
import json, traceback

class XMRigDatabase:
    """
    A class for handling database operations related to the XMRig miner.

    Attributes:
        _engines (Dict[str, Engine]): A dictionary to store database engines.
    """

    _engines = {}

    @classmethod
    def init_db(cls, db_url: str) -> Engine:
        """
        Initializes the database engine, if it already exists, it returns the existing engine.

        Args:
            db_url (str): Database URL for creating the engine.

        Returns:
            Engine: SQLAlchemy engine instance.

        Raises:
            XMRigDatabaseError: If an error occurs while initializing the database.
        """
        try:
            if db_url not in cls._engines:
                cls._engines[db_url] = create_engine(db_url)
            return cls._engines[db_url]
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred initializing the database:") from e
    
    @classmethod
    def get_db(cls, db_url: str) -> Engine:
        """
        Returns the database engine for the specified database URL.

        Args:
            db_url (str): Database URL for creating the engine.

        Returns:
            Engine: SQLAlchemy engine instance.

        Raises:
            XMRigDatabaseError: If the database engine does not exist.
        """
        try:
            return cls._engines[db_url]
        except KeyError as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"Database engine for '{db_url}' does not exist. Please initialize the database first.") from e

    @classmethod
    def check_table_exists(cls, db_url: str, table_name: str) -> bool:
        """
        Checks if the table exists in the database.

        Args:
            db_url (str): Database URL for creating the engine.
            table_name (str): Name of the table to check.

        Returns:
            bool: True if the table exists, False otherwise.

        Raises:
            XMRigDatabaseError: If an error occurs while checking if the table exists.
        """
        try:
            # Create an engine
            engine = cls.get_db(db_url)
            # Create an inspector
            inspector = inspect(engine)
            # Check if the table exists
            for i in inspector.get_table_names():
                if table_name in i:
                    return True
            return False
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred checking if the table exists:") from e
    
    @classmethod
    def insert_data_to_db(cls, json_data: Dict[str, Any], table_name: str, db_url: str) -> None:
        """
        Inserts JSON data into the specified database table.

        Args:
            json_data (Dict[str, Any]): JSON data to insert.
            table_name (str): Name of the table to insert data into.
            db_url (str): Database URL for creating the engine.

        Raises:
            XMRigDatabaseError: If an error occurs while inserting data into the database.
        """
        try:
            # Create a dataframe with the required columns and data
            data = {
                "timestamp": [datetime.now()],
                "full_json": [json.dumps(json_data)]
            }
            engine = cls.get_db(db_url)
            df = pd.DataFrame(data)
            # Insert data into the database
            df.to_sql(table_name, engine, if_exists="append", index=False)
            log.debug("Data inserted successfully")
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred inserting data to the database:") from e

    # TODO: Use this or fallback_to_db, ?
    @classmethod
    def retrieve_data_from_db(cls, db_url: str, table_name: str, selection: Union[str, List[str]] = "*", start_time: datetime = None, end_time: datetime = None, limit: int = None) -> Union[List[Dict[str, Any]], str]:
        """
        Retrieves data from the specified database table within the given timeframe.

        Args:
            db_url (str): Database URL for creating the engine.
            table_name (str): Name of the table to retrieve data from.
            selection (Union[str, List[str]], optional): Column(s) to select from the table. Defaults to "*".
            start_time (datetime, optional): Start time for the data retrieval. Defaults to None.
            end_time (datetime, optional): End time for the data retrieval. Defaults to None.
            limit (int, optional): Limit the number of rows retrieved. Defaults to None.

        Returns:
            Union[List[Dict[str, Any]], str]: List of dictionaries containing the retrieved data or "N/A" if the table does not exist.

        Raises:
            XMRigDatabaseError: If an error occurs while retrieving data from the database.
        """
        data = "N/A"
        try:
            if cls.check_table_exists(db_url, table_name) is True:
                engine = cls.get_db(db_url)
                if isinstance(selection, list):
                    selection = ", ".join(selection)
                query = f"SELECT {selection} FROM '{table_name}'"
                conditions = []
                params = {}
                if start_time:
                    conditions.append("timestamp >= :start_time")
                    params["start_time"] = start_time
                if end_time:
                    conditions.append("timestamp <= :end_time")
                    params["end_time"] = end_time
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                query += " ORDER BY timestamp DESC"
                if limit:
                    query += " LIMIT :limit"
                    params["limit"] = limit
                
                with engine.connect() as connection:
                    result = connection.execute(text(query), params)
                    data = [dict(row) for row in result]
            else:
                log.error(f"Table '{table_name}' does not exist in the database")
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred retrieving data from the database:") from e
        finally:
            return data
    
    @classmethod
    def fallback_to_db(cls, table_name: Union[str, List[str]], keys: List[Union[str, int]], db_url: str) -> Any:
        """
        Retrieves the data from the database using the provided table name.

        Args:
            table_name (Union[str, List[str]]): The name of the table or list of table names to use to retrieve the data.
            keys (List[Union[str, int]]): The keys to use to retrieve the data.
            db_url (str): The Database URL for creating the engine.

        Returns:
            Any: The retrieved data, or "N/A" if not available.

        Raises:
            XMRigDatabaseError: If an error occurs while retrieving data from the database.
        """
        column_name = "full_json"
        engine = cls.get_db(db_url)
        try:
            with engine.connect() as connection:
                # special handling for backends property, enables support for xmrig-mo fork
                if len(keys) < 1 and "backend" in table_name:
                    # get all backend tables and construct the response
                    backends = []
                    miner_name = table_name.split("-")[0].lstrip("'")
                    # Connect to the database and fetch the data in column_name from the table_name for each backend
                    if cls.check_table_exists(db_url, f"{miner_name}-cpu-backend"):
                        backends.append(json.loads(connection.execute(text(f"SELECT {column_name} FROM '{miner_name}-cpu-backend' ORDER BY timestamp DESC LIMIT 1")).fetchone()[0]))
                    if cls.check_table_exists(db_url, f"{miner_name}-opencl-backend"):
                        backends.append(json.loads(connection.execute(text(f"SELECT {column_name} FROM '{miner_name}-opencl-backend' ORDER BY timestamp DESC LIMIT 1")).fetchone()[0]))
                    if cls.check_table_exists(db_url, f"{miner_name}-cuda-backend"):
                        backends.append(json.loads(connection.execute(text(f"SELECT {column_name} FROM '{miner_name}-cuda-backend' ORDER BY timestamp DESC LIMIT 1")).fetchone()[0]))
                    return backends
                # default handling
                else:
                    # Connect to the database and fetch the data in column_name from the table_name
                    result = connection.execute(text(f"SELECT {column_name} FROM '{table_name}' ORDER BY timestamp DESC LIMIT 1"))
                    # Fetch the last item from the result
                    data = result.fetchone()
                    if data:
                        data = json.loads(data[0])
                    # if the first key is an int then that means we are dealing with the properties that require the
                    # backends tables, remove the first item from the keys list because the backends are stored in 
                    # individual tables
                    if isinstance(keys[0], int):
                        keys.pop(0)
                    # Use the list of keys/indices to access the correct data
                    if len(keys) > 0:
                        for key in keys:
                            data = data[key]
                    return data
            return "N/A"
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred retrieving data from the database:") from e
        finally:
            connection.close()

    @classmethod
    def delete_all_miner_data_from_db(cls, miner_name: str, db_url: str) -> None:
        """
        Deletes all tables related to a specific miner from the database.

        Args:
            miner_name (str): The unique name of the miner.
            db_url (str): Database URL for creating the engine.

        Raises:
            XMRigDatabaseError: If an error occurs while deleting the miner data from the database.
        """
        try:
            # Use quotes to avoid SQL syntax errors
            backends_table = f"{miner_name}-backends"
            config_table = f"{miner_name}-config"
            summary_table = f"{miner_name}-summary"
            engine = cls.get_db(db_url)
            with engine.connect() as connection:
                # Wrap the raw SQL strings in SQLAlchemy's `text` function so it isn't a raw string
                connection.execute(text(f"DROP TABLE IF EXISTS '{backends_table}'"))
                connection.execute(text(f"DROP TABLE IF EXISTS '{config_table}'"))
                connection.execute(text(f"DROP TABLE IF EXISTS '{summary_table}'"))
            log.debug(f"All tables for '{miner_name}' have been deleted from the database")
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred deleting miner '{miner_name}' from the database:") from e

# Define the public interface of the module
__all__ = ["XMRigDatabase"]