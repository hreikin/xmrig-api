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
from xmrig.models import Base, Summary, Resources, Memory, Results, Connection, CPU, Hashrate, Config, APIConfig, HTTPConfig, RandomXConfig, CPUConfig, OpenCLConfig, CUDAConfig, TLSConfig, DNSConfig, BenchmarkConfig, Backends, CPUBackend, OpenCLBackend, OpenCLPlatform, CUDABackend, CUDAVersions
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
                # Create instances of related models
                resources_data = json_data.get("resources", {})
                memory_data = resources_data.get("memory", {})
                memory = Memory(
                    full_json=memory_data,
                    free=memory_data.get("free"),
                    total=memory_data.get("total"),
                    resident_set_memory=memory_data.get("resident_set_memory"),
                )

                resources = Resources(
                    full_json=resources_data,
                    memory=memory,
                    load_average=resources_data.get("load_average"),
                    hardware_concurrency=resources_data.get("hardware_concurrency"),
                )

                results_data = json_data.get("results", {})
                results = Results(
                    full_json=results_data,
                    diff_current=results_data.get("diff_current"),
                    shares_good=results_data.get("shares_good"),
                    shares_total=results_data.get("shares_total"),
                    avg_time=results_data.get("avg_time"),
                    avg_time_ms=results_data.get("avg_time_ms"),
                    hashes_total=results_data.get("hashes_total"),
                    best=results_data.get("best"),
                )

                connection_data = json_data.get("connection", {})
                connection = Connection(
                    full_json=connection_data,
                    pool=connection_data.get("pool"),
                    ip=connection_data.get("ip"),
                    uptime=connection_data.get("uptime"),
                    uptime_ms=connection_data.get("uptime_ms"),
                    ping=connection_data.get("ping"),
                    failures=connection_data.get("failures"),
                    tls=connection_data.get("tls"),
                    tls_fingerprint=connection_data.get("tls-fingerprint"),
                    algo=connection_data.get("algo"),
                    diff=connection_data.get("diff"),
                    accepted=connection_data.get("accepted"),
                    rejected=connection_data.get("rejected"),
                    avg_time=connection_data.get("avg_time"),
                    avg_time_ms=connection_data.get("avg_time_ms"),
                    hashes_total=connection_data.get("hashes_total"),
                )

                cpu_data = json_data.get("cpu", {})
                cpu = CPU(
                    full_json=cpu_data,
                    brand=cpu_data.get("brand"),
                    family=cpu_data.get("family"),
                    model=cpu_data.get("model"),
                    stepping=cpu_data.get("stepping"),
                    proc_info=cpu_data.get("proc_info"),
                    aes=cpu_data.get("aes"),
                    avx2=cpu_data.get("avx2"),
                    x64=cpu_data.get("x64"),
                    bit_64=cpu_data.get("64_bit"),
                    l2=cpu_data.get("l2"),
                    l3=cpu_data.get("l3"),
                    cores=cpu_data.get("cores"),
                    threads=cpu_data.get("threads"),
                    packages=cpu_data.get("packages"),
                    nodes=cpu_data.get("nodes"),
                    backend=cpu_data.get("backend"),
                    msr=cpu_data.get("msr"),
                    assembly=cpu_data.get("assembly"),
                    arch=cpu_data.get("arch"),
                    flags=cpu_data.get("flags"),
                )

                hashrate_data = json_data.get("hashrate", {})
                hashrate = Hashrate(
                    full_json=hashrate_data,
                    total=hashrate_data.get("total"),
                    highest=hashrate_data.get("highest"),
                )

                # Create the main summary instance and set relationships
                summary = Summary(
                    miner_name=miner,
                    timestamp=cur_time,
                    full_json=json_data,
                    id=json_data.get("id"),
                    worker_id=json_data.get("worker_id"),
                    uptime=json_data.get("uptime"),
                    restricted=json_data.get("restricted"),
                    features=json_data.get("features"),
                    algo=json_data.get("algo"),
                    version=json_data.get("version"),
                    kind=json_data.get("kind"),
                    ua=json_data.get("ua"),
                    donate_level=json_data.get("donate_level"),
                    paused=json_data.get("paused"),
                    algorithms=json_data.get("algorithms"),
                    hugepages=json_data.get("hugepages"),
                    resources=resources,
                    results=results,
                    connection=connection,
                    cpu=cpu,
                    hashrate=hashrate,
                )

                # Add instances to the session
                session.add(memory)
                session.add(resources)
                session.add(results)
                session.add(connection)
                session.add(cpu)
                session.add(hashrate)
                session.add(summary)
            
            elif endpoint == "config":
                # Create instances of related models
                api_data = json_data.get("api", {})
                api = APIConfig(
                    full_json=api_data,
                    id=api_data.get("id"),
                    worker_id=api_data.get("worker-id"),
                )
                http_data = json_data.get("http", {})
                http = HTTPConfig(
                    full_json=http_data,
                    enabled=http_data.get("enabled"),
                    host=http_data.get("host"),
                    port=http_data.get("port"),
                    access_token=http_data.get("access-token"),
                    restricted=http_data.get("restricted"),
                )
                randomx_data = json_data.get("randomx", {})
                randomx = RandomXConfig(
                    full_json=randomx_data,
                    init=randomx_data.get("init"),
                    init_avx2=randomx_data.get("init-avx2"),
                    mode=randomx_data.get("mode"),
                    one_gb_pages=randomx_data.get("1gb-pages"),
                    rdmsr=randomx_data.get("rdmsr"),
                    wrmsr=randomx_data.get("wrmsr"),
                    cache_qos=randomx_data.get("cache_qos"),
                    numa=randomx_data.get("numa"),
                    scratchpad_prefetch_mode=randomx_data.get("scratchpad_prefetch_mode"),
                )
                cpu_data = json_data.get("cpu", {})
                cpu = CPUConfig(
                    full_json=cpu_data,
                    enabled=cpu_data.get("enabled"),
                    huge_pages=cpu_data.get("huge-pages"),
                    huge_pages_jit=cpu_data.get("huge-pages-jit"),
                    hw_aes=cpu_data.get("hw-aes"),
                    priority=cpu_data.get("priority"),
                    memory_pool=cpu_data.get("memory-pool"),
                    yield_value=cpu_data.get("yield"),
                    max_threads_hint=cpu_data.get("max-threads-hint"),
                    asm=cpu_data.get("asm"),
                    argon2_impl=cpu_data.get("argon2-impl"),
                )
                opencl_data = json_data.get("opencl", {})
                opencl = OpenCLConfig(
                    full_json=opencl_data,
                    enabled=opencl_data.get("enabled"),
                    cache=opencl_data.get("cache"),
                    loader=opencl_data.get("loader"),
                    platform=opencl_data.get("platform"),
                    adl=opencl_data.get("adl"),
                )
                cuda_data = json_data.get("cuda", {})
                cuda = CUDAConfig(
                    full_json=cuda_data,
                    enabled=cuda_data.get("enabled"),
                    loader=cuda_data.get("loader"),
                    nvml=cuda_data.get("nvml"),
                )
                tls_data = json_data.get("tls", {})
                tls = TLSConfig(
                    full_json=tls_data,
                    enabled=tls_data.get("enabled"),
                    protocols=tls_data.get("protocols"),
                    cert=tls_data.get("cert"),
                    cert_key=tls_data.get("cert_key"),
                    ciphers=tls_data.get("ciphers"),
                    ciphersuites=tls_data.get("ciphersuites"),
                    dhparam=tls_data.get("dhparam"),
                )
                dns_data = json_data.get("dns", {})
                dns = DNSConfig(
                    full_json=dns_data,
                    ipv6=dns_data.get("ipv6"),
                    ttl=dns_data.get("ttl"),
                )
                benchmark_data = json_data.get("benchmark", {})
                benchmark = BenchmarkConfig(
                    full_json=benchmark_data,
                    size=benchmark_data.get("size"),
                    algo=benchmark_data.get("algo"),
                    submit=benchmark_data.get("submit"),
                    verify=benchmark_data.get("verify"),
                    seed=benchmark_data.get("seed"),
                    hash_num=benchmark_data.get("hash-num"),
                )

                # Create the main config instance and set relationships
                config = Config(
                    miner_name=miner,
                    timestamp=cur_time,
                    full_json=json_data,
                    autosave=json_data.get("autosave"),
                    background=json_data.get("background"),
                    colors=json_data.get("colors"),
                    title=json_data.get("title"),
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
                    user_agent=json_data.get("user-agent"),
                    verbose=json_data.get("verbose"),
                    watch=json_data.get("watch"),
                    rebench_algo=json_data.get("rebench-algo"),
                    bench_algo_time=json_data.get("bench-algo-time"),
                    pause_on_battery=json_data.get("pause-on-battery"),
                    pause_on_active=json_data.get("pause-on-active"),
                    api=api,
                    http=http,
                    randomx=randomx,
                    cpu=cpu,
                    opencl=opencl,
                    cuda=cuda,
                    tls=tls,
                    dns=dns,
                    benchmark=benchmark,
                )

                # Add instances to the session
                session.add(api)
                session.add(http)
                session.add(randomx)
                session.add(cpu)
                session.add(opencl)
                session.add(cuda)
                session.add(tls)
                session.add(dns)
                session.add(benchmark)
                session.add(config)

            elif endpoint == "backends":
                # Create instances of related models
                cpu_backend_data = json_data[0]
                cpu_backend = CPUBackend(
                    full_json=cpu_backend_data,
                    type=cpu_backend_data.get("type"),
                    enabled=cpu_backend_data.get("enabled"),
                    algo=cpu_backend_data.get("algo"),
                    profile=cpu_backend_data.get("profile"),
                    hw_aes=cpu_backend_data.get("hw-aes"),
                    priority=cpu_backend_data.get("priority"),
                    msr=cpu_backend_data.get("msr"),
                    asm=cpu_backend_data.get("asm"),
                    argon2_impl=cpu_backend_data.get("argon2-impl"),
                    hugepages=cpu_backend_data.get("hugepages"),
                    memory=cpu_backend_data.get("memory"),
                    hashrate=cpu_backend_data.get("hashrate"),
                    threads=cpu_backend_data.get("threads"),
                )

                if len(json_data) > 1:
                    opencl_backend_data = json_data[1]
                    opencl_platform_data = opencl_backend_data.get("platform", {})
                    # create logic to handle the case where the platform is not present
                    if opencl_platform_data:
                        opencl_platform = OpenCLPlatform(
                            full_json=opencl_platform_data,
                            index=opencl_platform_data.get("index"),
                            profile=opencl_platform_data.get("profile"),
                            version=opencl_platform_data.get("version"),
                            name=opencl_platform_data.get("name"),
                            vendor=opencl_platform_data.get("vendor"),
                            extensions=opencl_platform_data.get("extensions"),
                        )
                    opencl_backend = OpenCLBackend(
                        full_json=opencl_backend_data,
                        type=opencl_backend_data.get("type"),
                        enabled=opencl_backend_data.get("enabled"),
                        algo=opencl_backend_data.get("algo"),
                        profile=opencl_backend_data.get("profile"),
                        hashrate=opencl_backend_data.get("hashrate"),
                        threads=opencl_backend_data.get("threads"),
                    )
                    if opencl_platform_data:
                        opencl_backend.platform = opencl_platform
                    
                    cuda_backend_data = json_data[2]
                    cuda_versions_data = cuda_backend_data.get("versions", {})
                    # create logic to handle the case where the versions is not present
                    if cuda_versions_data:
                        cuda_versions = CUDAVersions(
                            full_json=cuda_versions_data,
                            cuda_runtime=cuda_versions_data.get("cuda-runtime"),
                            cuda_driver=cuda_versions_data.get("cuda-driver"),
                            plugin=cuda_versions_data.get("plugin"),
                        )

                    cuda_backend = CUDABackend(
                        full_json=cuda_backend_data,
                        type=cuda_backend_data.get("type"),
                        enabled=cuda_backend_data.get("enabled"),
                        algo=cuda_backend_data.get("algo"),
                        profile=cuda_backend_data.get("profile"),
                        hashrate=cuda_backend_data.get("hashrate"),
                        threads=cuda_backend_data.get("threads"),
                    )
                    if cuda_versions_data:
                        cuda_backend.versions = cuda_versions
                # Create the main backends instance and set relationships
                backends = Backends(
                    miner_name=miner,
                    timestamp=cur_time,
                    full_json=json_data,
                    cpu=cpu_backend,
                )
                if len(json_data) > 1:
                    backends.opencl = opencl_backend
                    backends.cuda = cuda_backend

                # Add instances to the session
                session.add(cpu_backend)
                if len(json_data) > 1:
                    if opencl_platform_data:
                        session.add(opencl_platform)
                    session.add(opencl_backend)
                    if cuda_versions_data:
                        session.add(cuda_versions)
                    session.add(cuda_backend)
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