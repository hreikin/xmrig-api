from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Summary(Base):
    """
    ORM model for the 'summary' table.

    Attributes:
        uid (int): Primary key.
        miner_name (str): Name of the miner.
        timestamp (datetime): Timestamp of the record.
        full_json (dict): Full JSON data.
        id (str): ID of the summary.
        worker_id (str): Worker ID.
        uptime (int): Uptime of the miner.
        restricted (bool): Whether the miner is restricted.
        resources (dict): Resources data.
        resources_memory (dict): Memory resources data.
        resources_memory_free (int): Free memory.
        resources_memory_total (int): Total memory.
        resources_memory_rsm (int): RSM memory.
        resources_load_average (dict): Load average data.
        resources_hardware_concurrency (int): Hardware concurrency.
        features (dict): Features data.
        results (dict): Results data.
        results_diff_current (int): Current difficulty.
        results_shares_good (int): Good shares.
        results_shares_total (int): Total shares.
        results_avg_time (int): Average time.
        results_avg_time_ms (int): Average time in milliseconds.
        results_hashes_total (int): Total hashes.
        results_best (dict): Best results data.
        algo (str): Algorithm.
        connection (dict): Connection data.
        connection_pool (str): Connection pool.
        connection_ip (str): Connection IP.
        connection_uptime (int): Connection uptime.
        connection_uptime_ms (int): Connection uptime in milliseconds.
        connection_ping (int): Connection ping.
        connection_failures (int): Connection failures.
        connection_tls (dict): TLS connection data.
        connection_tls_fingerprint (dict): TLS fingerprint data.
        connection_algo (str): Connection algorithm.
        connection_diff (int): Connection difficulty.
        connection_accepted (int): Accepted connections.
        connection_rejected (int): Rejected connections.
        connection_avg_time (int): Average connection time.
        connection_avg_time_ms (int): Average connection time in milliseconds.
        connection_hashes_total (int): Total connection hashes.
        version (str): Version.
        kind (str): Kind.
        ua (str): User agent.
        cpu (dict): CPU data.
        cpu_brand (str): CPU brand.
        cpu_family (int): CPU family.
        cpu_model (int): CPU model.
        cpu_stepping (int): CPU stepping.
        cpu_proc_info (int): CPU processor info.
        cpu_aes (bool): CPU AES support.
        cpu_avx2 (bool): CPU AVX2 support.
        cpu_x64 (bool): CPU x64 support.
        cpu_64_bit (bool): CPU 64-bit support.
        cpu_l2 (int): CPU L2 cache size.
        cpu_l3 (int): CPU L3 cache size.
        cpu_cores (int): Number of CPU cores.
        cpu_threads (int): Number of CPU threads.
        cpu_packages (int): Number of CPU packages.
        cpu_nodes (int): Number of CPU nodes.
        cpu_backend (str): CPU backend.
        cpu_msr (str): CPU MSR.
        cpu_assembly (str): CPU assembly.
        cpu_arch (str): CPU architecture.
        cpu_flags (dict): CPU flags.
        donate_level (int): Donation level.
        paused (bool): Whether the miner is paused.
        algorithms (dict): Algorithms data.
        hashrate (dict): Hashrate data.
        hashrate_total (dict): Total hashrate.
        hashrate_highest (float): Highest hashrate.
        hugepages (dict): Hugepages data.
    """
    __tablename__ = "summary"
    uid = Column(Integer, primary_key=True)
    miner_name = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    full_json = Column(JSON)
    id = Column(String)
    worker_id = Column(String)
    uptime = Column(Integer)
    restricted = Column(Boolean)
    resources = Column(JSON)
    resources_memory = Column(JSON)
    resources_memory_free = Column(Integer)
    resources_memory_total = Column(Integer)
    resources_memory_rsm = Column(Integer)
    resources_load_average = Column(JSON)
    resources_hardware_concurrency = Column(Integer)
    features = Column(JSON)
    results = Column(JSON)
    results_diff_current = Column(Integer)
    results_shares_good = Column(Integer)
    results_shares_total = Column(Integer)
    results_avg_time = Column(Integer)
    results_avg_time_ms = Column(Integer)
    results_hashes_total = Column(Integer)
    results_best = Column(JSON)
    algo = Column(String)
    connection = Column(JSON)
    connection_pool = Column(String)
    connection_ip = Column(String)
    connection_uptime = Column(Integer)
    connection_uptime_ms = Column(Integer)
    connection_ping = Column(Integer)
    connection_failures = Column(Integer)
    connection_tls = Column(JSON)
    connection_tls_fingerprint = Column(JSON)
    connection_algo = Column(String)
    connection_diff = Column(Integer)
    connection_accepted = Column(Integer)
    connection_rejected = Column(Integer)
    connection_avg_time = Column(Integer)
    connection_avg_time_ms = Column(Integer)
    connection_hashes_total = Column(Integer)
    version = Column(String)
    kind = Column(String)
    ua = Column(String)
    cpu = Column(JSON)
    cpu_brand = Column(String)
    cpu_family = Column(Integer)
    cpu_model = Column(Integer)
    cpu_stepping = Column(Integer)
    cpu_proc_info = Column(Integer)
    cpu_aes = Column(Boolean)
    cpu_avx2 = Column(Boolean)
    cpu_x64 = Column(Boolean)
    cpu_64_bit = Column(Boolean)
    cpu_l2 = Column(Integer)
    cpu_l3 = Column(Integer)
    cpu_cores = Column(Integer)
    cpu_threads = Column(Integer)
    cpu_packages = Column(Integer)
    cpu_nodes = Column(Integer)
    cpu_backend = Column(String)
    cpu_msr = Column(String)
    cpu_assembly = Column(String)
    cpu_arch = Column(String)
    cpu_flags = Column(JSON)
    donate_level = Column(Integer)
    paused = Column(Boolean)
    algorithms = Column(JSON)
    hashrate = Column(JSON)
    hashrate_total = Column(JSON)
    hashrate_highest = Column(Float)
    hugepages = Column(JSON)

class Config(Base):
    """
    ORM model for the 'config' table.

    Attributes:
        uid (int): Primary key.
        miner_name (str): Name of the miner.
        timestamp (datetime): Timestamp of the record.
        full_json (dict): Full JSON data.
        api (dict): API data.
        api_id (str): API ID.
        api_worker_id (str): API worker ID.
        http (dict): HTTP data.
        http_enabled (bool): Whether HTTP is enabled.
        http_host (str): HTTP host.
        http_port (int): HTTP port.
        http_access_token (str): HTTP access token.
        http_restricted (bool): Whether HTTP is restricted.
        autosave (bool): Whether autosave is enabled.
        background (bool): Whether background mode is enabled.
        colors (bool): Whether colors are enabled.
        title (dict): Title data.
        randomx (dict): RandomX data.
        randomx_init (int): RandomX initialization.
        randomx_init_avx2 (int): RandomX AVX2 initialization.
        randomx_mode (str): RandomX mode.
        randomx_1gb_pages (bool): Whether RandomX 1GB pages are enabled.
        randomx_rdmsr (bool): Whether RandomX RDMSR is enabled.
        randomx_wrmsr (dict): RandomX WRMSR data.
        randomx_cache_qos (bool): Whether RandomX cache QoS is enabled.
        randomx_numa (bool): Whether RandomX NUMA is enabled.
        randomx_scratchpad_prefetch_mode (int): RandomX scratchpad prefetch mode.
        cpu (dict): CPU data.
        cpu_enabled (bool): Whether CPU is enabled.
        cpu_huge_pages (dict): CPU huge pages data.
        cpu_huge_pages_jit (bool): Whether CPU huge pages JIT is enabled.
        cpu_hw_aes (bool): Whether CPU hardware AES is enabled.
        cpu_priority (int): CPU priority.
        cpu_memory_pool (dict): CPU memory pool data.
        cpu_yield (bool): Whether CPU yield is enabled.
        cpu_max_threads_hint (int): CPU max threads hint.
        cpu_asm (dict): CPU assembly data.
        cpu_argon2_impl (str): CPU Argon2 implementation.
        opencl (dict): OpenCL data.
        opencl_enabled (bool): Whether OpenCL is enabled.
        opencl_cache (bool): Whether OpenCL cache is enabled.
        opencl_loader (str): OpenCL loader.
        opencl_platform (dict): OpenCL platform data.
        opencl_adl (bool): Whether OpenCL ADL is enabled.
        cuda (dict): CUDA data.
        cuda_enabled (bool): Whether CUDA is enabled.
        cuda_loader (str): CUDA loader.
        cuda_nvml (bool): Whether CUDA NVML is enabled.
        donate_level (int): Donation level.
        donate_over_proxy (int): Donation over proxy.
        log_file (str): Log file.
        pools (dict): Pools data.
        print_time (int): Print time.
        health_print_time (int): Health print time.
        dmi (bool): Whether DMI is enabled.
        retries (int): Number of retries.
        retry_pause (int): Retry pause.
        syslog (bool): Whether syslog is enabled.
        tls (dict): TLS data.
        tls_enabled (bool): Whether TLS is enabled.
        tls_protocols (str): TLS protocols.
        tls_cert (str): TLS certificate.
        tls_cert_key (str): TLS certificate key.
        tls_ciphers (str): TLS ciphers.
        tls_ciphersuites (str): TLS ciphersuites.
        tls_dhparam (str): TLS DH parameters.
        dns (dict): DNS data.
        dns_ipv6 (bool): Whether DNS IPv6 is enabled.
        dns_ttl (int): DNS TTL.
        user_agent (str): User agent.
        verbose (int): Verbose level.
        watch (bool): Whether watch mode is enabled.
        rebench_algo (bool): Whether rebench algorithm is enabled.
        bench_algo_time (int): Benchmark algorithm time.
        pause_on_battery (bool): Whether to pause on battery.
        pause_on_active (dict): Pause on active data.
        benchmark (dict): Benchmark data.
        benchmark_size (str): Benchmark size.
        benchmark_algo (str): Benchmark algorithm.
        benchmark_submit (bool): Whether to submit benchmark.
        benchmark_verify (str): Benchmark verification.
        benchmark_seed (str): Benchmark seed.
        benchmark_hash (str): Benchmark hash.
    """
    __tablename__ = "config"
    uid = Column(Integer, primary_key=True)
    miner_name = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    full_json = Column(JSON)
    api = Column(JSON)
    api_id = Column(String)
    api_worker_id = Column(String)
    http = Column(JSON)
    http_enabled = Column(Boolean)
    http_host = Column(String)
    http_port = Column(Integer)
    http_access_token = Column(String)
    http_restricted = Column(Boolean)
    autosave = Column(Boolean)
    background = Column(Boolean)
    colors = Column(Boolean)
    title = Column(JSON)
    randomx = Column(JSON)
    randomx_init = Column(Integer)
    randomx_init_avx2 = Column(Integer)
    randomx_mode = Column(String)
    randomx_1gb_pages = Column(Boolean)
    randomx_rdmsr = Column(Boolean)
    randomx_wrmsr = Column(JSON)
    randomx_cache_qos = Column(Boolean)
    randomx_numa = Column(Boolean)
    randomx_scratchpad_prefetch_mode = Column(Integer)
    cpu = Column(JSON)
    cpu_enabled = Column(Boolean)
    cpu_huge_pages = Column(JSON)
    cpu_huge_pages_jit = Column(Boolean)
    cpu_hw_aes = Column(Boolean)
    cpu_priority = Column(Integer)
    cpu_memory_pool = Column(JSON)
    cpu_yield = Column(Boolean)
    cpu_max_threads_hint = Column(Integer)
    cpu_asm = Column(JSON)
    cpu_argon2_impl = Column(String)
    opencl = Column(JSON)
    opencl_enabled = Column(Boolean)
    opencl_cache = Column(Boolean)
    opencl_loader = Column(String)
    opencl_platform = Column(JSON)
    opencl_adl = Column(Boolean)
    cuda = Column(JSON)
    cuda_enabled = Column(Boolean)
    cuda_loader = Column(String)
    cuda_nvml = Column(Boolean)
    donate_level = Column(Integer)
    donate_over_proxy = Column(Integer)
    log_file = Column(String)
    pools = Column(JSON)
    print_time = Column(Integer)
    health_print_time = Column(Integer)
    dmi = Column(Boolean)
    retries = Column(Integer)
    retry_pause = Column(Integer)
    syslog = Column(Boolean)
    tls = Column(JSON)
    tls_enabled = Column(Boolean)
    tls_protocols = Column(String)
    tls_cert = Column(String)
    tls_cert_key = Column(String)
    tls_ciphers = Column(String)
    tls_ciphersuites = Column(String)
    tls_dhparam = Column(String)
    dns = Column(JSON)
    dns_ipv6 = Column(Boolean)
    dns_ttl = Column(Integer)
    user_agent = Column(String)
    verbose = Column(Integer)
    watch = Column(Boolean)
    rebench_algo = Column(Boolean)
    bench_algo_time = Column(Integer)
    pause_on_battery = Column(Boolean)
    pause_on_active = Column(JSON)
    benchmark = Column(JSON)
    benchmark_size = Column(String)
    benchmark_algo = Column(String)
    benchmark_submit = Column(Boolean)
    benchmark_verify = Column(String)
    benchmark_seed = Column(String)
    benchmark_hash = Column(String)

class Backends(Base):
    """
    ORM model for the 'backends' table.

    Attributes:
        uid (int): Primary key.
        miner_name (str): Name of the miner.
        timestamp (datetime): Timestamp of the record.
        full_json (dict): Full JSON data.
        cpu (dict): CPU data.
        cpu_type (str): CPU type.
        cpu_enabled (bool): Whether CPU is enabled.
        cpu_algo (str): CPU algorithm.
        cpu_profile (str): CPU profile.
        cpu_hw_aes (bool): Whether CPU hardware AES is enabled.
        cpu_priority (int): CPU priority.
        cpu_msr (bool): Whether CPU MSR is enabled.
        cpu_asm (str): CPU assembly.
        cpu_argon2_impl (str): CPU Argon2 implementation.
        cpu_hugepages (dict): CPU hugepages data.
        cpu_memory (int): CPU memory.
        cpu_hashrate (dict): CPU hashrate data.
        cpu_threads (dict): CPU threads data.
        opencl (dict): OpenCL data.
        opencl_type (str): OpenCL type.
        opencl_enabled (bool): Whether OpenCL is enabled.
        opencl_algo (str): OpenCL algorithm.
        opencl_profile (str): OpenCL profile.
        opencl_platform (dict): OpenCL platform data.
        opencl_platform_index (int): OpenCL platform index.
        opencl_platform_profile (str): OpenCL platform profile.
        opencl_platform_version (str): OpenCL platform version.
        opencl_platform_name (str): OpenCL platform name.
        opencl_platform_vendor (str): OpenCL platform vendor.
        opencl_platform_extensions (str): OpenCL platform extensions.
        opencl_hashrate (dict): OpenCL hashrate data.
        opencl_threads (dict): OpenCL threads data.
        cuda (dict): CUDA data.
        cuda_type (str): CUDA type.
        cuda_enabled (bool): Whether CUDA is enabled.
        cuda_algo (str): CUDA algorithm.
        cuda_profile (str): CUDA profile.
        cuda_versions (dict): CUDA versions data.
        cuda_versions_cuda_runtime (str): CUDA runtime version.
        cuda_versions_cuda_driver (str): CUDA driver version.
        cuda_versions_plugin (str): CUDA plugin version.
        cuda_hashrate (dict): CUDA hashrate data.
        cuda_threads (dict): CUDA threads data.
    """
    __tablename__ = "backends"
    uid = Column(Integer, primary_key=True)
    miner_name = Column(String)
    timestamp = Column(DateTime, default=datetime.now)
    full_json = Column(JSON)
    cpu = Column(JSON)
    cpu_type = Column(String)
    cpu_enabled = Column(Boolean)
    cpu_algo = Column(String)
    cpu_profile = Column(String)
    cpu_hw_aes = Column(Boolean)
    cpu_priority = Column(Integer)
    cpu_msr = Column(Boolean)
    cpu_asm = Column(String)
    cpu_argon2_impl = Column(String)
    cpu_hugepages = Column(JSON)
    cpu_memory = Column(Integer)
    cpu_hashrate = Column(JSON)
    cpu_threads = Column(JSON)
    opencl = Column(JSON)
    opencl_type = Column(String)
    opencl_enabled = Column(Boolean)
    opencl_algo = Column(String)
    opencl_profile = Column(String)
    opencl_platform = Column(JSON)
    opencl_platform_index = Column(Integer)
    opencl_platform_profile = Column(String)
    opencl_platform_version = Column(String)
    opencl_platform_name = Column(String)
    opencl_platform_vendor = Column(String)
    opencl_platform_extensions = Column(String)
    opencl_hashrate = Column(JSON)
    opencl_threads = Column(JSON)
    cuda = Column(JSON)
    cuda_type = Column(String)
    cuda_enabled = Column(Boolean)
    cuda_algo = Column(String)
    cuda_profile = Column(String)
    cuda_versions = Column(JSON)
    cuda_versions_cuda_runtime = Column(String)
    cuda_versions_cuda_driver = Column(String)
    cuda_versions_plugin = Column(String)
    cuda_hashrate = Column(JSON)
    cuda_threads = Column(JSON)

# Define the public interface of the module
__all__ = ["Summary", "Config", "Backends"]