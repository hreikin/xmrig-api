class XMRig:
    def __init__(self, ip, port, access_token: str = None):
        self._ip = ip
        self._port = port
        self._access_token = access_token
        self._base_url = f"http://{ip}:{port}/2"

        self._summary_url = f"{self._base_url}/summary"
        self._stats_url = f"{self._base_url}/stats"
        self._config_url = f"{self._base_url}/config"
        self._version_url = f"{self._base_url}/version"
        self._log_url = f"{self._base_url}/log"
        self._backends_url = f"{self._base_url}/backends"
        self._workers_url = f"{self._base_url}/workers"
        self._results_url = f"{self._base_url}/results"
        self._connections_url = f"{self._base_url}/connections"
        self._threads_url = f"{self._base_url}/threads"