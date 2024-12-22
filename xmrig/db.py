"""
XMRig Database module.

This module handles database initialization and operations for storing and managing miner data.
It includes functions for initializing the database, inserting data, and deleting miner-related tables.
"""

import json
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from datetime import datetime
from xmrig.logger import log

_engines = {}

def _init_db(db_url: str) -> Engine:
    """
    Initializes the database engine.

    Args:
        db_url (str): Database URL.

    Returns:
        Engine: SQLAlchemy engine instance.
    """
    if db_url not in _engines:
        _engines[db_url] = create_engine(db_url)
    return _engines[db_url]

def _insert_data_to_db(json_data: dict, table_name: str, engine: Engine) -> None:
    """
    Inserts JSON data into the specified database table.

    Args:
        json_data (dict): JSON data to insert.
        table_name (str): Name of the table to insert data into.
        engine (Engine): SQLAlchemy engine instance.
    """
    # Normalize nested JSON
    df = pd.json_normalize(json_data)

    # Convert lists to JSON strings
    for column in df.columns:
        if df[column].apply(lambda x: isinstance(x, list)).any():
            df[column] = df[column].apply(json.dumps)

    # Add a timestamp column
    df.insert(0, 'timestamp', datetime.now())

    # Insert data into the database
    df.to_sql(table_name, engine, if_exists='append', index=False)

    log.debug("Data inserted successfully")

def _delete_miner_from_db(miner_name: str, engine: Engine) -> None:
    """
    Deletes all tables related to a specific miner from the database.

    Args:
        miner_name (str): The unique name of the miner.
        engine (Engine): SQLAlchemy engine instance.
    """
    # Use quotes to avoid SQL syntax errors
    backends_table = f"'{miner_name}-backends'"
    config_table = f"'{miner_name}-config'"
    summary_table = f"'{miner_name}-summary'"
    with engine.connect() as connection:
        # Wrap the raw SQL strings in SQLAlchemy's `text` function so it isn't a raw string
        connection.execute(text(f"DROP TABLE IF EXISTS {backends_table}"))
        connection.execute(text(f"DROP TABLE IF EXISTS {config_table}"))
        connection.execute(text(f"DROP TABLE IF EXISTS {summary_table}"))

    log.debug(f"All tables for '{miner_name}' have been deleted from the database")