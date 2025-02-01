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
from sqlalchemy.orm import sessionmaker
from xmrig.exceptions import XMRigDatabaseError
from xmrig.logger import log
from xmrig.models import Base, Summary, Config, Backends
from datetime import datetime
from typing import Dict, Any, Union, List
import pandas as pd
import traceback

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
                engine = create_engine(db_url)
                Base.metadata.create_all(engine)
                cls._engines[db_url] = engine
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
    def insert_data_to_db(cls, json_data: Dict[str, Any], miner: str, endpoint: str, db_url: str) -> None:
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
            engine = cls.get_db(db_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            cur_time = datetime.now()
            if endpoint == "summary":
                resources_data = json_data.get("resources", {})
                memory_data = resources_data.get("memory", {})
                results_data = json_data.get("results", {})
                connection_data = json_data.get("connection", {})
                cpu_data = json_data.get("cpu", {})
                hashrate_data = json_data.get("hashrate", {})
                # Create the main summary instance
                summary = Summary(
                    miner_name=miner,
                    timestamp=cur_time,
                    full_json=json_data,
                    id=json_data.get("id"),
                    worker_id=json_data.get("worker_id"),
                    uptime=json_data.get("uptime"),
                    restricted=json_data.get("restricted"),
                    resources = resources_data,
                    resources_memory = memory_data,
                    resources_memory_free=memory_data.get("free"),
                    resources_memory_total=memory_data.get("total"),
                    resources_memory_rsm=memory_data.get("resident_set_memory"),
                    resources_load_average=resources_data.get("load_average"),
                    resources_hardware_concurrency=resources_data.get("hardware_concurrency"),
                    features=json_data.get("features"),
                    results = results_data,
                    results_diff_current = results_data.get("diff_current"),
                    results_shares_good = results_data.get("shares_good"),
                    results_shares_total = results_data.get("shares_total"),
                    results_avg_time = results_data.get("avg_time"),
                    results_avg_time_ms = results_data.get("avg_time_ms"),
                    results_hashes_total = results_data.get("hashes_total"),
                    results_best = results_data.get("best"),
                    algo=json_data.get("algo"),
                    connection = connection_data,
                    connection_ip=connection_data.get("ip"),
                    connection_uptime=connection_data.get("uptime"),
                    connection_uptime_ms=connection_data.get("uptime_ms"),
                    connection_ping=connection_data.get("ping"),
                    connection_failures=connection_data.get("failures"),
                    connection_tls=connection_data.get("tls"),
                    connection_tls_fingerprint=connection_data.get("tls-fingerprint"),
                    connection_algo=connection_data.get("algo"),
                    connection_diff=connection_data.get("diff"),
                    connection_accepted=connection_data.get("accepted"),
                    connection_rejected=connection_data.get("rejected"),
                    connection_avg_time=connection_data.get("avg_time"),
                    connection_avg_time_ms=connection_data.get("avg_time_ms"),
                    connection_hashes_total=connection_data.get("hashes_total"),
                    version=json_data.get("version"),
                    kind=json_data.get("kind"),
                    ua=json_data.get("ua"),
                    cpu = cpu_data,
                    cpu_brand=cpu_data.get("brand"),
                    cpu_family=cpu_data.get("family"),
                    cpu_model=cpu_data.get("model"),
                    cpu_stepping=cpu_data.get("stepping"),
                    cpu_proc_info=cpu_data.get("proc_info"),
                    cpu_aes=cpu_data.get("aes"),
                    cpu_avx2=cpu_data.get("avx2"),
                    cpu_x64=cpu_data.get("x64"),
                    cpu_64_bit=cpu_data.get("64_bit"),
                    cpu_l2=cpu_data.get("l2"),
                    cpu_l3=cpu_data.get("l3"),
                    cpu_cores=cpu_data.get("cores"),
                    cpu_threads=cpu_data.get("threads"),
                    cpu_packages=cpu_data.get("packages"),
                    cpu_nodes=cpu_data.get("nodes"),
                    cpu_backend=cpu_data.get("backend"),
                    cpu_msr=cpu_data.get("msr"),
                    cpu_assembly=cpu_data.get("assembly"),
                    cpu_arch=cpu_data.get("arch"),
                    cpu_flags=cpu_data.get("flags"),
                    donate_level=json_data.get("donate_level"),
                    paused=json_data.get("paused"),
                    algorithms=json_data.get("algorithms"),
                    hashrate = hashrate_data,
                    hashrate_total=hashrate_data.get("total"),
                    hashrate_highest=hashrate_data.get("highest"),
                    hugepages=json_data.get("hugepages"),
                )
                # Add instance to the session
                session.add(summary)
            elif endpoint == "config":
                api_data = json_data.get("api", {})
                http_data = json_data.get("http", {})
                randomx_data = json_data.get("randomx", {})
                cpu_data = json_data.get("cpu", {})
                opencl_data = json_data.get("opencl", {})
                cuda_data = json_data.get("cuda", {})
                tls_data = json_data.get("tls", {})
                dns_data = json_data.get("dns", {})
                benchmark_data = json_data.get("benchmark", {})
                # Create the main config instance
                config = Config(
                    miner_name=miner,
                    timestamp=cur_time,
                    full_json=json_data,
                    api = api_data,
                    api_id=api_data.get("id"),
                    api_worker_id=api_data.get("worker-id"),
                    http = http_data,
                    http_enabled=http_data.get("enabled"),
                    http_host=http_data.get("host"),
                    http_port=http_data.get("port"),
                    http_access_token=http_data.get("access-token"),
                    http_restricted=http_data.get("restricted"),
                    autosave=json_data.get("autosave"),
                    background=json_data.get("background"),
                    colors=json_data.get("colors"),
                    title=json_data.get("title"),
                    randomx = randomx_data,
                    randomx_init=randomx_data.get("init"),
                    randomx_init_avx2=randomx_data.get("init-avx2"),
                    randomx_mode=randomx_data.get("mode"),
                    randomx_1gb_pages=randomx_data.get("1gb-pages"),
                    randomx_rdmsr=randomx_data.get("rdmsr"),
                    randomx_wrmsr=randomx_data.get("wrmsr"),
                    randomx_cache_qos=randomx_data.get("cache_qos"),
                    randomx_numa=randomx_data.get("numa"),
                    randomx_scratchpad_prefetch_mode=randomx_data.get("scratchpad_prefetch_mode"),
                    cpu = cpu_data,
                    cpu_enabled=cpu_data.get("enabled"),
                    cpu_huge_pages=cpu_data.get("huge-pages"),
                    cpu_huge_pages_jit=cpu_data.get("huge-pages-jit"),
                    cpu_hw_aes=cpu_data.get("hw-aes"),
                    cpu_priority=cpu_data.get("priority"),
                    cpu_memory_pool=cpu_data.get("memory-pool"),
                    cpu_yield=cpu_data.get("yield"),
                    cpu_max_threads_hint=cpu_data.get("max-threads-hint"),
                    cpu_asm=cpu_data.get("asm"),
                    cpu_argon2_impl=cpu_data.get("argon2-impl"),
                    opencl = opencl_data,
                    opencl_enabled=opencl_data.get("enabled"),
                    opencl_cache=opencl_data.get("cache"),
                    opencl_loader=opencl_data.get("loader"),
                    opencl_platform=opencl_data.get("platform"),
                    opencl_adl=opencl_data.get("adl"),
                    cuda = cuda_data,
                    cuda_enabled=cuda_data.get("enabled"),
                    cuda_loader=cuda_data.get("loader"),
                    cuda_nvml=cuda_data.get("nvml"),
                    donate_level=json_data.get("donate-level"),
                    donate_over_proxy=json_data.get("donate-over-proxy"),
                    log_file=json_data.get("log-file"),
                    pools=json_data.get("pools"),
                    print_time=json_data.get("print-time"),
                    health_print_time=json_data.get("health-print-time"),
                    dmi=json_data.get("dmi"),
                    retries=json_data.get("retries"),
                    retry_pause=json_data.get("retry-pause"),
                    syslog=json_data.get("syslog"),
                    tls = tls_data,
                    tls_enabled=tls_data.get("enabled"),
                    tls_protocols=tls_data.get("protocols"),
                    tls_cert=tls_data.get("cert"),
                    tls_cert_key=tls_data.get("cert_key"),
                    tls_ciphers=tls_data.get("ciphers"),
                    tls_ciphersuites=tls_data.get("ciphersuites"),
                    tls_dhparam=tls_data.get("dhparam"),
                    dns = dns_data,
                    dns_ipv6=dns_data.get("ipv6"),
                    dns_ttl=dns_data.get("ttl"),
                    user_agent=json_data.get("user-agent"),
                    verbose=json_data.get("verbose"),
                    watch=json_data.get("watch"),
                    rebench_algo=json_data.get("rebench-algo"),
                    bench_algo_time=json_data.get("bench-algo-time"),
                    pause_on_battery=json_data.get("pause-on-battery"),
                    pause_on_active=json_data.get("pause-on-active"),
                    benchmark = benchmark_data,
                    benchmark_size=benchmark_data.get("size"),
                    benchmark_algo=benchmark_data.get("algo"),
                    benchmark_submit=benchmark_data.get("submit"),
                    benchmark_verify=benchmark_data.get("verify"),
                    benchmark_seed=benchmark_data.get("seed"),
                    benchmark_hash_num=benchmark_data.get("hash-num"),
                )
                # Add instance to the session
                session.add(config)
            elif endpoint == "backends":
                if len(json_data) == 1:
                    cpu_backend_data = json_data[0]
                    # Create the main backends instance for xmrig
                    backends = Backends(
                        miner_name=miner,
                        timestamp=cur_time,
                        full_json=json_data,
                        cpu=cpu_backend_data,
                        cpu_type=cpu_backend_data.get("type"),
                        cpu_enabled=cpu_backend_data.get("enabled"),
                        cpu_algo=cpu_backend_data.get("algo"),
                        cpu_profile=cpu_backend_data.get("profile"),
                        cpu_hw_aes=cpu_backend_data.get("hw-aes"),
                        cpu_priority=cpu_backend_data.get("priority"),
                        cpu_msr=cpu_backend_data.get("msr"),
                        cpu_asm=cpu_backend_data.get("asm"),
                        cpu_argon2_impl=cpu_backend_data.get("argon2-impl"),
                        cpu_hugepages=cpu_backend_data.get("hugepages"),
                        cpu_memory=cpu_backend_data.get("memory"),
                        cpu_hashrate=cpu_backend_data.get("hashrate"),
                        cpu_threads=cpu_backend_data.get("threads"),
                    )
                elif len(json_data) > 1:
                    cpu_backend_data = json_data[0]
                    opencl_backend_data = json_data[1]
                    cuda_backend_data = json_data[2]
                    # Create the main backends instance for xmrig-mo
                    backends = Backends(
                        miner_name=miner,
                        timestamp=cur_time,
                        full_json=json_data,
                        cpu=cpu_backend_data,
                        cpu_type=cpu_backend_data.get("type"),
                        cpu_enabled=cpu_backend_data.get("enabled"),
                        cpu_algo=cpu_backend_data.get("algo"),
                        cpu_profile=cpu_backend_data.get("profile"),
                        cpu_hw_aes=cpu_backend_data.get("hw-aes"),
                        cpu_priority=cpu_backend_data.get("priority"),
                        cpu_msr=cpu_backend_data.get("msr"),
                        cpu_asm=cpu_backend_data.get("asm"),
                        cpu_argon2_impl=cpu_backend_data.get("argon2-impl"),
                        cpu_hugepages=cpu_backend_data.get("hugepages"),
                        cpu_memory=cpu_backend_data.get("memory"),
                        cpu_hashrate=cpu_backend_data.get("hashrate"),
                        cpu_threads=cpu_backend_data.get("threads"),
                        opencl = opencl_backend_data,
                        opencl_type=opencl_backend_data.get("type"),
                        opencl_enabled=opencl_backend_data.get("enabled"),
                        opencl_algo=opencl_backend_data.get("algo"),
                        opencl_profile=opencl_backend_data.get("profile"),
                        opencl_platform=opencl_backend_data.get("platform"),
                        opencl_platform_index=opencl_backend_data["platform"].get("index") if opencl_backend_data.get("platform") else None,
                        opencl_platform_profile=opencl_backend_data["platform"].get("profile") if opencl_backend_data.get("platform") else None,
                        opencl_platform_version=opencl_backend_data["platform"].get("version") if opencl_backend_data.get("platform") else None,
                        opencl_platform_name=opencl_backend_data["platform"].get("name") if opencl_backend_data.get("platform") else None,
                        opencl_platform_vendor=opencl_backend_data["platform"].get("vendor") if opencl_backend_data.get("platform") else None,
                        opencl_platform_extensions=opencl_backend_data["platform"].get("extensions") if opencl_backend_data.get("platform") else None,
                        opencl_hashrate=opencl_backend_data.get("hashrate"),
                        opencl_threads=opencl_backend_data.get("threads"),
                        cuda = cuda_backend_data,
                        cuda_type=cuda_backend_data.get("type"),
                        cuda_enabled=cuda_backend_data.get("enabled"),
                        cuda_algo=cuda_backend_data.get("algo"),
                        cuda_profile=cuda_backend_data.get("profile"),
                        cuda_versions=cuda_backend_data.get("versions"),
                        cuda_versions_cuda_runtime=cuda_backend_data["versions"].get("cuda_runtime") if cuda_backend_data.get("versions") else None,
                        cuda_versions_cuda_driver=cuda_backend_data["versions"].get("cuda_driver") if cuda_backend_data.get("versions") else None,
                        cuda_versions_plugin=cuda_backend_data["versions"].get("plugin") if cuda_backend_data.get("versions") else None,
                        cuda_hashrate=cuda_backend_data.get("hashrate"),
                        cuda_threads=cuda_backend_data.get("threads"),
                    )
                # Add instance to the session
                session.add(backends)
            # Commit the session
            session.commit()
        except Exception as e:
            session.rollback()
            raise XMRigDatabaseError(e, traceback.format_exc(), f"An error occurred inserting data to the database:") from e
        finally:
            session.close()
    
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