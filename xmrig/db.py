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
            # Create a DataFrame with the additional metadata columns
            metadata = pd.DataFrame({
                "timestamp": [pd.Timestamp.now()],
                "full_json": [json.dumps(json_data)]
            })
            # Check if json_data is a list of dictionaries (backends endpoint)
            if isinstance(json_data, list) and all(isinstance(item, dict) for item in json_data):
                # Flatten the list of dictionaries and prefix column names with their position in the list
                flattened_data = {}
                for idx, item in enumerate(json_data):
                    for key, value in item.items():
                        flattened_data[f"{idx}.{key}"] = value
                json_data = flattened_data
            # Flatten the JSON data
            df = pd.json_normalize(json_data, sep=".")
            # Convert list-type values to JSON strings
            for col in df.columns:
                df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
            # Concatenate the additional columns with the original DataFrame
            df = pd.concat([metadata, df], axis=1)
            engine = cls.get_db(db_url)
            df.to_sql(table_name, engine, if_exists="append", index=False)
            log.debug("Data inserted successfully")
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred inserting data to the database:") from e
    
    @classmethod
    def retrieve_data_from_db(cls, db_url: str, table_name: str, selection: Union[str, List[str]] = "*", start_time: datetime = None, end_time: datetime = None, limit: int = 1) -> Union[List[Dict[str, Any]], str]:
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
                # use single quotes for the f-string and double quotes for the selection and table name
                query = f'SELECT "{selection}" FROM "{table_name}"'
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
                df = pd.read_sql(query, engine, params=params)
                if not df.empty:
                    data = df.to_dict(orient='records')
                else:
                    data = "N/A"
            else:
                log.error(f"Table '{table_name}' does not exist in the database")
        except Exception as e:
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred retrieving data from the database:") from e
        finally:
            return data

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