"""
XMRig Helpers module.

This module provides helper functions and classes for the XMRig API interactions and operations.
It includes:

- Logging configuration for the XMRig API.
- Custom exception classes for handling specific API errors.
- Database initialization and operations for storing and managing miner data.
- Functions for inserting data into the database.
- Functions for deleting miner-related tables from the database.
"""

import logging
import json
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from datetime import datetime
from typing import Dict, Any

log = logging.getLogger("XMRigAPI")

_engines = {}

class XMRigAPIError(Exception):
    """
    Exception raised when a general error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the API issue.
    """

    def __init__(self, message: str = "An error occurred with the XMRig API."):
        """
        Initialize the API error.

        Args:
            message (str): Error message. Defaults to a generic API error message.
        """
        self.message = message
        super().__init__(self.message)

class XMRigAuthorizationError(Exception):
    """
    Exception raised when an authorization error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the authorization issue.
    """

    def __init__(self, message: str = "Access token is required but not provided. Please provide a valid access token."):
        """
        Initialize the authorization error.

        Args:
            message (str): Error message. Defaults to a generic authorization error message.
        """
        self.message = message
        super().__init__(self.message)

class XMRigConnectionError(Exception):
    """
    Exception raised when a connection error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the connection issue.
    """

    def __init__(self, message: str = "Failed to connect to the XMRig API. Please check the IP, port, and network connection."):
        """
        Initialize the connection error.

        Args:
            message (str): Error message. Defaults to a generic connection error message.
        """
        self.message = message
        super().__init__(self.message)

# TODO: Move to XMRigManager class as a static method
def _init_db(db_url: str) -> Engine:
    """
    Initializes the database engine.

    Args:
        db_url (str): Database URL.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    try:
        if db_url not in _engines:
            _engines[db_url] = create_engine(db_url)
        return _engines[db_url]
    except Exception as e:
        log.error(f"An error occurred initializing the database: {e}")
        raise XMRigAPIError() from e

# TODO: Move to XMRigProperties class
def _insert_data_to_db(json_data: Dict[str, Any], table_name: str, engine: Engine) -> None:
    """
    Inserts JSON data into the specified database table.

    Args:
        json_data (Dict[str, Any]): JSON data to insert.
        table_name (str): Name of the table to insert data into.
        engine (Engine): SQLAlchemy engine instance.
    """
    try:
        # Normalize nested JSON
        df = pd.json_normalize(json_data)
        # "pools"
        if "pools" in json_data:
            pools = json_data["pools"]
            if pools:
                # Normalize pools data
                pools_df = pd.json_normalize(pools)
                # Rename columns to avoid conflicts with the main dataframe
                pools_df.columns = [f"pool.{col}" for col in pools_df.columns]
                # Merge the pools data with the main dataframe
                df = pd.concat([df, pools_df], axis=1)
        # "threads"
        if "threads" in json_data:
            threads = json_data["threads"]
            if threads:
                for thread_item in threads:
                    prefix = threads.index(thread_item)
                    threads_df = pd.json_normalize(thread_item)
                    # Rename columns to avoid conflicts with the main dataframe
                    threads_df.columns = [f"thread.{prefix}.{col}" for col in threads_df.columns]
                    # Merge the threads data with the main dataframe
                    df = pd.concat([df, threads_df], axis=1)
        # Convert lists to JSON strings
        for column in df.columns:
            if df[column].apply(lambda x: isinstance(x, list)).any():
                df[column] = df[column].apply(json.dumps)
        # Add a timestamp column and a column for a copy of the full unflattened json data
        df.insert(0, 'timestamp', datetime.now())
        df.insert(1, 'full_json', json.dumps(json_data))
        # Insert data into the database
        df.to_sql(table_name, engine, if_exists='append', index=False)
        log.debug("Data inserted successfully")
    except Exception as e:
        log.error(f"An error occurred inserting data to the database: {e}")
        raise XMRigAPIError() from e

def _delete_all_miner_data_from_db(miner_name: str, engine: Engine) -> None:
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
