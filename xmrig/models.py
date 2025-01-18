from sqlalchemy import Column, Integer, String, Boolean, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Summary(Base):
    __tablename__ = 'summary'
    
    id = Column(String, primary_key=True)
    worker_id = Column(String)
    uptime = Column(Integer)
    restricted = Column(Boolean)
    resources_id = Column(Integer, ForeignKey('resources.id'))
    features = Column(JSON)
    results_id = Column(Integer, ForeignKey('results.id'))
    algo = Column(String)
    connection_id = Column(Integer, ForeignKey('connection.id'))
    version = Column(String)
    kind = Column(String)
    ua = Column(String)
    cpu_id = Column(Integer, ForeignKey('cpu.id'))
    donate_level = Column(Integer)
    paused = Column(Boolean)
    algorithms = Column(JSON)
    hashrate_id = Column(Integer, ForeignKey('hashrate.id'))
    hugepages = Column(JSON)

    resources = relationship("Resources", back_populates="summary")
    results = relationship("Results", back_populates="summary")
    connection = relationship("Connection", back_populates="summary")
    cpu = relationship("CPU", back_populates="summary")
    hashrate = relationship("Hashrate", back_populates="summary")

class Resources(Base):
    __tablename__ = 'resources'
    
    id = Column(Integer, primary_key=True)
    memory = Column(JSON)
    load_average = Column(JSON)
    hardware_concurrency = Column(Integer)
    summary = relationship("Summary", back_populates="resources")

class Results(Base):
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    diff_current = Column(Integer)
    shares_good = Column(Integer)
    shares_total = Column(Integer)
    avg_time = Column(Integer)
    avg_time_ms = Column(Integer)
    hashes_total = Column(Integer)
    best = Column(JSON)
    summary = relationship("Summary", back_populates="results")

class Connection(Base):
    __tablename__ = 'connection'
    
    id = Column(Integer, primary_key=True)
    pool = Column(String)
    ip = Column(String)
    uptime = Column(Integer)
    uptime_ms = Column(Integer)
    ping = Column(Integer)
    failures = Column(Integer)
    tls = Column(String)
    tls_fingerprint = Column(String)
    algo = Column(String)
    diff = Column(Integer)
    accepted = Column(Integer)
    rejected = Column(Integer)
    avg_time = Column(Integer)
    avg_time_ms = Column(Integer)
    hashes_total = Column(Integer)
    summary = relationship("Summary", back_populates="connection")

class CPU(Base):
    __tablename__ = 'cpu'
    
    id = Column(Integer, primary_key=True)
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
    __tablename__ = 'hashrate'
    
    id = Column(Integer, primary_key=True)
    total = Column(JSON)
    highest = Column(Float)
    summary = relationship("Summary", back_populates="hashrate")

class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    autosave = Column(Boolean)
    background = Column(Boolean)
    colors = Column(Boolean)
    title = Column(Boolean)
    api_id = Column(Integer, ForeignKey('api_config.id'))
    http_id = Column(Integer, ForeignKey('http_config.id'))
    randomx_id = Column(Integer, ForeignKey('randomx_config.id'))
    cpu_id = Column(Integer, ForeignKey('cpu_config.id'))

    api = relationship("APIConfig")
    http = relationship("HTTPConfig")
    randomx = relationship("RandomXConfig")
    cpu = relationship("CPUConfig")

class APIConfig(Base):
    __tablename__ = 'api_config'
    id = Column(Integer, primary_key=True)
    worker_id = Column(String)

class HTTPConfig(Base):
    __tablename__ = 'http_config'
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    host = Column(String)
    port = Column(Integer)
    access_token = Column(String)
    restricted = Column(Boolean)

class RandomXConfig(Base):
    __tablename__ = 'randomx_config'
    id = Column(Integer, primary_key=True)
    init = Column(Integer)
    init_avx2 = Column(Integer)
    mode = Column(String)
    one_gb_pages = Column(Boolean, name="1gb_pages")
    rdmsr = Column(Boolean)
    wrmsr = Column(Boolean)
    cache_qos = Column(Boolean)
    numa = Column(Boolean)
    scratchpad_prefetch_mode = Column(Integer)

class CPUConfig(Base):
    __tablename__ = 'cpu_config'
    id = Column(Integer, primary_key=True)
    enabled = Column(Boolean)
    huge_pages = Column(Boolean)
    huge_pages_jit = Column(Boolean)
    hw_aes = Column(Boolean)
    priority = Column(Integer)
    memory_pool = Column(Boolean)

class Backend(Base):
    __tablename__ = 'backends'
    
    id = Column(Integer, primary_key=True)
    type = Column(String)
    enabled = Column(Boolean)
    algo = Column(String)
    profile = Column(String)
    platform_id = Column(Integer, ForeignKey('platforms.id'))
    platform = relationship("Platform", back_populates="backends")
    hashrate = Column(JSON)
    threads = relationship("Thread", back_populates="backend")

class Platform(Base):
    __tablename__ = 'platforms'
    
    id = Column(Integer, primary_key=True)
    index = Column(Integer)
    profile = Column(String)
    version = Column(String)
    name = Column(String)
    vendor = Column(String)
    extensions = Column(String)
    backends = relationship("Backend", back_populates="platform")

class Thread(Base):
    __tablename__ = 'threads'
    
    id = Column(Integer, primary_key=True)
    backend_id = Column(Integer, ForeignKey('backends.id'))
    backend = relationship("Backend", back_populates="threads")
    index = Column(Integer)
    intensity = Column(Integer)
    worksize = Column(Integer)
    threads = Column(JSON)
    unroll = Column(Integer)
    affinity = Column(Integer)
    hashrate = Column(JSON)
    board = Column(String)