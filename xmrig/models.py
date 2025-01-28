from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# // TODO: Add Memory ORM model with relationship to Resources
# // TODO: Add copy of data in JSON format to the sub-tables
# // TODO: Finish models for, opencl, cuda, tls, and dns in config.json
# // TODO: Fix models so all backends data is contained within the same table
# // TODO: Double check all values from the json are included within the models
# // TODO: Switch id/uid in models to be consistent with the JSON data
# // TODO: Double check all values have correct types based on the XMRig documentation for config.json 
# // TODO: and the JSON data for summary and backends
# // TODO: Check if the types are correct for the marked columns in the models (those columns can hold 
# // TODO: multiple types) - use JSON type for those columns ?
# // TODO: Add a BenchmarkConfig model based on benchmark section of the documentation

Base = declarative_base()

class Summary(Base):
    __tablename__ = "summary"
    full_json = Column(JSON)
    id = Column(String)
    worker_id = Column(String)
    uptime = Column(Integer)
    restricted = Column(Boolean)
    resources_uid = Column(Integer, ForeignKey("resources.uid"))
    resources = relationship("Resources", back_populates="summary")
    features = Column(JSON)
    results_uid = Column(Integer, ForeignKey("results.uid"))
    results = relationship("Results", back_populates="summary")
    algo = Column(String)
    connection_uid = Column(Integer, ForeignKey("connection.uid"))
    connection = relationship("Connection", back_populates="summary")
    version = Column(String)
    kind = Column(String)
    ua = Column(String)
    cpu_uid = Column(Integer, ForeignKey("cpu.uid"))
    cpu = relationship("CPU", back_populates="summary")
    donate_level = Column(Integer)
    paused = Column(Boolean)
    algorithms = Column(JSON)
    hashrate_uid = Column(Integer, ForeignKey("hashrate.uid"))
    hashrate = relationship("Hashrate", back_populates="summary")
    hugepages = Column(JSON)

class Resources(Base):
    __tablename__ = "resources"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    memory_uid = Column(Integer, ForeignKey("memory.uid"))
    memory = relationship("Memory", back_populates="resources")
    load_average = Column(JSON)
    hardware_concurrency = Column(Integer)

    summary = relationship("Summary", back_populates="resources")

class Memory(Base):
    __tablename__ = "memory"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    free = Column(Integer)
    total = Column(Integer)
    resident_set_memory = Column(Integer)
    
    resources = relationship("Resources", back_populates="memory")

class Results(Base):
    __tablename__ = "results"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    diff_current = Column(Integer)
    shares_good = Column(Integer)
    shares_total = Column(Integer)
    avg_time = Column(Integer)
    avg_time_ms = Column(Integer)
    hashes_total = Column(Integer)
    best = Column(JSON)

    summary = relationship("Summary", back_populates="results")

class Connection(Base):
    __tablename__ = "connection"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    pool = Column(String)
    ip = Column(String)
    uptime = Column(Integer)
    uptime_ms = Column(Integer)
    ping = Column(Integer)
    failures = Column(Integer)
    tls = Column(JSON)
    tls_fingerprint = Column(JSON)
    algo = Column(String)
    diff = Column(Integer)
    accepted = Column(Integer)
    rejected = Column(Integer)
    avg_time = Column(Integer)
    avg_time_ms = Column(Integer)
    hashes_total = Column(Integer)

    summary = relationship("Summary", back_populates="connection")

class CPU(Base):
    __tablename__ = "cpu"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    brand = Column(String)
    family = Column(Integer)
    model = Column(Integer)
    stepping = Column(Integer)
    proc_info = Column(Integer)
    aes = Column(Boolean)
    avx2 = Column(Boolean)
    x64 = Column(Boolean)
    bit_64 = Column(Boolean)
    l2 = Column(Integer)
    l3 = Column(Integer)
    cores = Column(Integer)
    threads = Column(Integer)
    packages = Column(Integer)
    nodes = Column(Integer)
    backend = Column(String)
    msr = Column(String)
    assembly = Column(String)
    arch = Column(String)
    flags = Column(JSON)

    summary = relationship("Summary", back_populates="cpu")

class Hashrate(Base):
    __tablename__ = "hashrate"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    total = Column(JSON)
    highest = Column(Float)

    summary = relationship("Summary", back_populates="hashrate")

class Config(Base):
    __tablename__ = "config"
    full_json = Column(JSON)
    api_uid = Column(Integer, ForeignKey("api_config.uid"))
    api = relationship("APIConfig", back_populates="config")
    http_uid = Column(Integer, ForeignKey("http_config.uid"))
    http = relationship("HTTPConfig", back_populates="config")
    autosave = Column(Boolean)
    background = Column(Boolean)
    colors = Column(Boolean)
    title = Column(JSON)
    randomx_uid = Column(Integer, ForeignKey("randomx_config.uid"))
    randomx = relationship("RandomXConfig", back_populates="config")
    cpu_uid = Column(Integer, ForeignKey("cpu_config.uid"))
    cpu = relationship("CPUConfig", back_populates="config")
    opencl_uid = Column(Integer, ForeignKey("opencl_config.uid"))
    opencl = relationship("OpenCLConfig", back_populates="config")
    cuda_uid = Column(Integer, ForeignKey("cuda_config.uid"))
    cuda = relationship("CUDAConfig", back_populates="config")
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
    tls_uid = Column(Integer, ForeignKey("tls_config.uid"))
    tls = relationship("TLSConfig", back_populates="config")
    dns_uid = Column(Integer, ForeignKey("dns_config.uid"))
    dns = relationship("DNSConfig", back_populates="config")
    user_agent = Column(String)
    verbose = Column(Integer)
    watch = Column(Boolean)
    rebench_algo = Column(Boolean)
    bench_algo_time = Column(Integer)
    pause_on_battery = Column(Boolean)
    pause_on_active = Column(JSON)
    benchmark_uid = Column(Integer, ForeignKey("benchmark_config.uid"))
    benchmark = relationship("BenchmarkConfig", back_populates="config")

class APIConfig(Base):
    __tablename__ = "api_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    id = Column(String)
    worker_id = Column(String)

    api = relationship("Config", back_populates="api")

class HTTPConfig(Base):
    __tablename__ = "http_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    enabled = Column(Boolean)
    host = Column(String)
    port = Column(Integer)
    access_token = Column(String)
    restricted = Column(Boolean)

    http = relationship("Config", back_populates="http")

class RandomXConfig(Base):
    __tablename__ = "randomx_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    init = Column(Integer)
    init_avx2 = Column(Integer)
    mode = Column(String)
    one_gb_pages = Column(Boolean)
    rdmsr = Column(Boolean)
    wrmsr = Column(JSON)
    cache_qos = Column(Boolean)
    numa = Column(Boolean)
    scratchpad_prefetch_mode = Column(Integer)

    randomx = relationship("Config", back_populates="randomx")

class CPUConfig(Base):
    __tablename__ = "cpu_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    enabled = Column(Boolean)
    huge_pages = Column(JSON)
    huge_pages_jit = Column(Boolean)
    hw_aes = Column(Boolean)
    priority = Column(Integer)
    memory_pool = Column(JSON)
    yield_value = Column(Boolean)
    max_threads_hint = Column(Integer)
    asm = Column(JSON)
    argon2_impl = Column(String)

    cpu = relationship("Config", back_populates="cpu")

class OpenCLConfig(Base):
    __tablename__ = "opencl_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    enabled = Column(Boolean)
    cache = Column(Boolean)
    loader = Column(String)
    platform = Column(JSON)
    adl = Column(Boolean)

    opencl = relationship("Config", back_populates="opencl")

class CudaConfig(Base):
    __tablename__ = "cuda_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    enabled = Column(Boolean)
    loader = Column(String)
    nvml = Column(Boolean)

    cuda = relationship("Config", back_populates="cuda")

class TLSConfig(Base):
    __tablename__ = "tls_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    enabled = Column(Boolean)
    protocols = Column(String)
    cert = Column(String)
    cert_key = Column(String)
    ciphers = Column(String)
    ciphersuites = Column(String)
    dhparam = Column(String)

    tls = relationship("Config", back_populates="tls")

class DNSConfig(Base):
    __tablename__ = "dns_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    ipv6 = Column(Boolean)
    ttl = Column(Integer)

    dns = relationship("Config", back_populates="dns")

class BenchmarkConfig(Base):
    __tablename__ = "benchmark_config"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    size = Column(String)
    algo = Column(String)
    submit = Column(Boolean)
    verify = Column(String)
    seed = Column(String)
    hash_num = Column(String)

    benchmark = relationship("Config", back_populates="benchmark")

class Backends(Base):
    __tablename__ = "backends"
    full_json = Column(JSON)
    cpu_uid = Column(Integer, ForeignKey("cpu_backend.uid"))
    cpu = relationship("CPUBackend", back_populates="backends")
    opencl_uid = Column(Integer, ForeignKey("opencl_backend.uid"))
    opencl = relationship("OpenCLBackend", back_populates="backends")
    cuda_uid = Column(Integer, ForeignKey("cuda_backend.uid"))
    cuda = relationship("CUDABackend", back_populates="backends")

class CPUBackend(Base):
    __tablename__ = "cpu_backend"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    type = Column(String)
    enabled = Column(Boolean)
    algo = Column(String)
    profile = Column(String)
    hw_aes = Column(Boolean)
    priority = Column(Integer)
    msr = Column(Boolean)
    asm = Column(String)
    argon2_impl = Column(String)
    hugepages = Column(JSON)
    memory = Column(Integer)
    hashrate = Column(JSON)
    threads = Column(JSON)
    
    backends = relationship("Backends", back_populates="cpu")

class OpenCLBackend(Base):
    __tablename__ = "opencl_backend"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    type = Column(String)
    enabled = Column(Boolean)
    algo = Column(String)
    profile = Column(String)
    platform_uid = Column(Integer, ForeignKey("opencl_platform.uid"))
    platform = relationship("OpenCLPlatform", back_populates="opencl")
    hashrate = Column(JSON)
    threads = Column(JSON)
    
    backends = relationship("Backends", back_populates="opencl")

class OpenCLPlatform(Base):
    __tablename__ = "opencl_platform"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    index = Column(Integer)
    profile = Column(String)
    version = Column(String)
    name = Column(String)
    vendor = Column(String)
    extensions = Column(String)

    opencl_backend = relationship("OpenCLBackend", back_populates="platform")

class CUDABackend(Base):
    __tablename__ = "cuda_backend"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    type = Column(String)
    enabled = Column(Boolean)
    algo = Column(String)
    profile = Column(String)
    versions_uid = Column(Integer, ForeignKey("cuda_versions.uid"))
    versions = relationship("CUDAVersions", back_populates="cuda")
    hashrate = Column(JSON)
    threads = Column(JSON)
    
    backends = relationship("Backends", back_populates="cuda")

class CUDAVersions(Base):
    __tablename__ = "cuda_versions"
    uid = Column(Integer, primary_key=True)
    full_json = Column(JSON)
    cuda_runtime = Column(String)
    cuda_driver = Column(String)
    plugin = Column(String)

    cuda_backend = relationship("CUDABackend", back_populates="versions")