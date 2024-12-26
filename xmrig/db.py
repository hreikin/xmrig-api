from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from xmrig.helpers import log, XMRigAPIError
from datetime import datetime
from typing import Dict, Any, Union, List
import pandas as pd
import json

# TODO: More refactoring required (probably elsewhere, maybe here as well) to get methods to work with the rest of the codebase
# TODO: Refactor methods after making @staticmethods so they can be called without an instance of the class, move db_url to init_db, and remove self from all @staticmethods
# TODO: leave init_db as a class method and make it set the engine value rather than return it, create a @staticmethod to return the engine, and use that in the other methods

class XMRigDatabase:
    def __init__(self, db_url: str):
        self._engines = {}
        self._db_url = db_url

    def init_db(self) -> Engine:
        """
        Initializes the database engine.

        Returns:
            Engine: SQLAlchemy engine instance.
        """
        try:
            if self._db_url not in self._engines:
                self._engines[self._db_url] = create_engine(self._db_url)
            return self._engines[self._db_url]
        except Exception as e:
            log.error(f"An error occurred initializing the database: {e}")
            raise XMRigAPIError() from e
    
    @staticmethod
    def insert_data_to_db(self, json_data: Dict[str, Any], table_name: str, engine: Engine) -> None:
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
                    pools_df.columns = [f"pools.{col}" for col in pools_df.columns]
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
    
    # TODO: Finish implementing this method.
    @staticmethod
    def get_data_from_db(self, table_name: Union[str, List[str]], keys: List[Union[str, int]], engine: Engine) -> None:
        """
        Retrieves the data from the database using the provided table name.

        Args:
            table_name (Union[str, List[str]]): The name of the table or list of table names to use to retrieve the data.
            keys (List[Union[str, int]]): The keys to use to retrieve the data.
            engine (Engine): The SQLAlchemy engine instance.
        """
        column_name = ""
        # handle column names for config.json "pools"
        # needs properties creating for config.json datapoints
        if "pools" in keys:
            pass
        # handle column names for backends.json "threads"
        elif "threads" in keys:
            column_name += "threads"
        # handle default column names
        else:
            for key in keys:
                if not isinstance(key, int):
                    column_name += f"{key}."
            column_name = column_name[:-1]

        return "N/A"

    @staticmethod
    def delete_all_miner_data_from_db(self, miner_name: str, engine: Engine) -> None:
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