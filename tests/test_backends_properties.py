import unittest, json
from xmrig_api import XMRigAPI

class TestBackendsProperties(unittest.TestCase):
    """
    Tests that ensure the properties relating to the summary endpoint return the expected value. 
    These tests require a running instance of XMRig to be configured but are run against cached 
    data.
    """
    def setUp(self):
        """
        Instantiate the XMRig API client and feed it cached data to run the tests with.
        """
        self.api = XMRigAPI(ip="127.0.0.1", port="37841", access_token="SECRET")

        ##### Comment this block out to run against live data.
        with open("example-api/example-backends.json", "r") as f:
            self.mock_backends = json.load(f)
        self.api._backends_response = self.mock_backends
        #####

    def test_backends_property(self):
        """Test that the 'backends' property returns a list containing dictionaries with a 'type' key."""
        result = self.api.backends
        self.assertIsInstance(result, list)
        self.assertIn("type", result[0])

    def test_enabled_backends_property(self):
        """Test that the 'enabled_backends' property returns a list."""
        result = self.api.enabled_backends
        self.assertIsInstance(result, list)

    def test_be_cpu_type_property(self):
        """Test that the 'be_cpu_type' property returns a string."""
        result = self.api.be_cpu_type
        self.assertIsInstance(result, str)

    def test_be_cpu_enabled_property(self):
        """Test that the 'be_cpu_enabled' property returns a boolean."""
        result = self.api.be_cpu_enabled
        self.assertIsInstance(result, bool)

    def test_be_cpu_algo_property(self):
        """Test that the 'be_cpu_algo' property returns a string."""
        result = self.api.be_cpu_algo
        self.assertIsInstance(result, str)

    def test_be_cpu_profile_property(self):
        """Test that the 'be_cpu_profile' property returns a string."""
        result = self.api.be_cpu_profile
        self.assertIsInstance(result, str)

    def test_be_cpu_hw_aes_property(self):
        """Test that the 'be_cpu_hw_aes' property returns a boolean."""
        result = self.api.be_cpu_hw_aes
        self.assertIsInstance(result, bool)

    def test_be_cpu_priority_property(self):
        """Test that the 'be_cpu_priority' property returns an integer."""
        result = self.api.be_cpu_priority
        self.assertIsInstance(result, int)

    def test_be_cpu_msr_property(self):
        """Test that the 'be_cpu_msr' property returns a boolean."""
        result = self.api.be_cpu_msr
        self.assertIsInstance(result, bool)

    def test_be_cpu_asm_property(self):
        """Test that the 'be_cpu_asm' property returns a string."""
        result = self.api.be_cpu_asm
        self.assertIsInstance(result, str)

    def test_be_cpu_argon2_impl_property(self):
        """Test that the 'be_cpu_argon2_impl' property returns a string."""
        result = self.api.be_cpu_argon2_impl
        self.assertIsInstance(result, str)

    def test_be_cpu_hugepages_property(self):
        """Test that the 'be_cpu_hugepages' property returns a list."""
        result = self.api.be_cpu_hugepages
        self.assertIsInstance(result, list)

    def test_be_cpu_memory_property(self):
        """Test that the 'be_cpu_memory' property returns an integer."""
        result = self.api.be_cpu_memory
        self.assertIsInstance(result, int)

    def test_be_cpu_hashrates_property(self):
        """Test that the 'be_cpu_hashrates' property returns a list."""
        result = self.api.be_cpu_hashrates
        self.assertIsInstance(result, list)

    def test_be_cpu_hashrate_10s_property(self):
        """Test that the 'be_cpu_hashrate_10s' property returns a float or None."""
        result = self.api.be_cpu_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_hashrate_1m_property(self):
        """Test that the 'be_cpu_hashrate_1m' property returns a float or None."""
        result = self.api.be_cpu_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_hashrate_15m_property(self):
        """Test that the 'be_cpu_hashrate_15m' property returns a float or None."""
        result = self.api.be_cpu_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))  

    def test_be_cpu_threads_property(self):
        """Test that the 'be_cpu_threads' property returns a list."""
        result = self.api.be_cpu_threads
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_intensity_property(self):
        """Test that the 'be_cpu_threads_intensity' property returns a list."""
        result = self.api.be_cpu_threads_intensity
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_affinity_property(self):
        """Test that the 'be_cpu_threads_affinity' property returns a list."""
        result = self.api.be_cpu_threads_affinity
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_av_property(self):
        """Test that the 'be_cpu_threads_av' property returns a list."""
        result = self.api.be_cpu_threads_av
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_10s_property(self):
        """Test that the 'be_cpu_threads_hashrates_10s' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_10s
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_1m_property(self):
        """Test that the 'be_cpu_threads_hashrates_1m' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_1m
        self.assertIsInstance(result, list)

    def test_be_cpu_threads_hashrates_15m_property(self):
        """Test that the 'be_cpu_threads_hashrates_15m' property returns a list."""
        result = self.api.be_cpu_threads_hashrates_15m
        self.assertIsInstance(result, list)
    
    #######################################################################

    def test_be_opencl_type_property(self):
        """Test that the 'be_opencl_type' property returns a string."""
        result = self.api.be_opencl_type
        self.assertIsInstance(result, str)

    def test_be_opencl_enabled_property(self):
        """Test that the 'be_opencl_enabled' property returns a boolean."""
        result = self.api.be_opencl_enabled
        self.assertIsInstance(result, bool)

    def test_be_opencl_algo_property(self):
        """Test that the 'be_opencl_algo' property returns a string."""
        result = self.api.be_opencl_algo
        self.assertIsInstance(result, str)

    def test_be_opencl_profile_property(self):
        """Test that the 'be_opencl_profile' property returns a string."""
        result = self.api.be_opencl_profile
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_property(self):
        """Test that the 'be_opencl_platform' property returns a dictionary."""
        result = self.api.be_opencl_platform
        self.assertIsInstance(result, dict)

    def test_be_opencl_platform_index_property(self):
        """Test that the 'be_opencl_platform_index' property returns an integer."""
        result = self.api.be_opencl_platform_index
        self.assertIsInstance(result, int)

    def test_be_opencl_platform_profile_property(self):
        """Test that the 'be_opencl_platform_profile' property returns a string."""
        result = self.api.be_opencl_platform_profile
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_version_property(self):
        """Test that the 'be_opencl_platform_version' property returns a string."""
        result = self.api.be_opencl_platform_version
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_name_property(self):
        """Test that the 'be_opencl_platform_name' property returns a string."""
        result = self.api.be_opencl_platform_name
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_vendor_property(self):
        """Test that the 'be_opencl_platform_vendor' property returns a string."""
        result = self.api.be_opencl_platform_vendor
        self.assertIsInstance(result, str)

    def test_be_opencl_platform_extensions_property(self):
        """Test that the 'be_opencl_platform_extensions' property returns a string."""
        result = self.api.be_opencl_platform_extensions
        self.assertIsInstance(result, str)

    def test_be_opencl_hashrates_property(self):
        """Test that the 'be_opencl_hashrates' property returns a list."""
        result = self.api.be_opencl_hashrates
        self.assertIsInstance(result, list)

    def test_be_opencl_hashrate_10s_property(self):
        """Test that the 'be_opencl_hashrate_10s' property returns a float or None."""
        result = self.api.be_opencl_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_hashrate_1m_property(self):
        """Test that the 'be_opencl_hashrate_1m' property returns a float or None."""
        result = self.api.be_opencl_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_hashrate_15m_property(self):
        """Test that the 'be_opencl_hashrate_15m' property returns a float or None."""
        result = self.api.be_opencl_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_property(self):
        """Test that the 'be_opencl_threads' property returns a dictionary."""
        result = self.api.be_opencl_threads
        self.assertIsInstance(result, dict)

    def test_be_opencl_threads_index_property(self):
        """Test that the 'be_opencl_threads_index' property returns an integer."""
        result = self.api.be_opencl_threads_index
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_intensity_property(self):
        """Test that the 'be_opencl_threads_intensity' property returns an integer."""
        result = self.api.be_opencl_threads_intensity
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_worksize_property(self):
        """Test that the 'be_opencl_threads_worksize' property returns an integer."""
        result = self.api.be_opencl_threads_worksize
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_amount_property(self):
        """Test that the 'be_opencl_threads_amount' property returns a list."""
        result = self.api.be_opencl_threads_amount
        self.assertIsInstance(result, list)

    def test_be_opencl_threads_unroll_property(self):
        """Test that the 'be_opencl_threads_unroll' property returns an integer."""
        result = self.api.be_opencl_threads_unroll
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_affinity_property(self):
        """Test that the 'be_opencl_threads_affinity' property returns an integer."""
        result = self.api.be_opencl_threads_affinity
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_hashrates_property(self):
        """Test that the 'be_opencl_threads_hashrates' property returns a list."""
        result = self.api.be_opencl_threads_hashrates
        self.assertIsInstance(result, list)

    def test_be_opencl_threads_hashrates_10s_property(self):
        """Test that the 'be_opencl_threads_hashrates_10s' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_hashrates_1m_property(self):
        """Test that the 'be_opencl_threads_hashrates_1m' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_hashrates_15m_property(self):
        """Test that the 'be_opencl_threads_hashrates_15m' property returns a float or None."""
        result = self.api.be_opencl_threads_hashrates_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_opencl_threads_board_property(self):
        """Test that the 'be_opencl_threads_board' property returns a string."""
        result = self.api.be_opencl_threads_board
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_name_property(self):
        """Test that the 'be_opencl_threads_name' property returns a string."""
        result = self.api.be_opencl_threads_name
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_bus_id_property(self):
        """Test that the 'be_opencl_threads_bus_id' property returns a string."""
        result = self.api.be_opencl_threads_bus_id
        self.assertIsInstance(result, str)

    def test_be_opencl_threads_cu_property(self):
        """Test that the 'be_opencl_threads_cu' property returns an integer."""
        result = self.api.be_opencl_threads_cu
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_global_mem_property(self):
        """Test that the 'be_opencl_threads_global_mem' property returns an integer."""
        result = self.api.be_opencl_threads_global_mem
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_property(self):
        """Test that the 'be_opencl_threads_health' property returns a dictionary."""
        result = self.api.be_opencl_threads_health
        self.assertIsInstance(result, dict)

    def test_be_opencl_threads_health_temp_property(self):
        """Test that the 'be_opencl_threads_health_temp' property returns an integer."""
        result = self.api.be_opencl_threads_health_temp
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_power_property(self):
        """Test that the 'be_opencl_threads_health_power' property returns an integer."""
        result = self.api.be_opencl_threads_health_power
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_clock_property(self):
        """Test that the 'be_opencl_threads_health_clock' property returns an integer."""
        result = self.api.be_opencl_threads_health_clock
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_mem_clock_property(self):
        """Test that the 'be_opencl_threads_health_mem_clock' property returns an integer."""
        result = self.api.be_opencl_threads_health_mem_clock
        self.assertIsInstance(result, int)

    def test_be_opencl_threads_health_rpm_property(self):
        """Test that the 'be_opencl_threads_health_rpm' property returns an integer."""
        result = self.api.be_opencl_threads_health_rpm
        self.assertIsInstance(result, int)

    #######################################################################

    def test_be_cuda_type_property(self):
        """Test that the 'be_cuda_type' property returns a string."""
        result = self.api.be_cuda_type
        self.assertIsInstance(result, str)

    def test_be_cuda_enabled_property(self):
        """Test that the 'be_cuda_enabled' property returns a boolean."""
        result = self.api.be_cuda_enabled
        self.assertIsInstance(result, bool)

    def test_be_cuda_algo_property(self):
        """Test that the 'be_cuda_algo' property returns a string."""
        result = self.api.be_cuda_algo
        self.assertIsInstance(result, str)

    def test_be_cuda_profile_property(self):
        """Test that the 'be_cuda_profile' property returns a string."""
        result = self.api.be_cuda_profile
        self.assertIsInstance(result, str)

    def test_be_cuda_versions_property(self):
        """Test that the 'be_cuda_versions' property returns a dictionary."""
        result = self.api.be_cuda_versions
        self.assertIsInstance(result, dict)

    def test_be_cuda_runtime_property(self):
        """Test that the 'be_cuda_runtime' property returns a string."""
        result = self.api.be_cuda_runtime
        self.assertIsInstance(result, str)

    def test_be_cuda_driver_property(self):
        """Test that the 'be_cuda_driver' property returns a string."""
        result = self.api.be_cuda_driver
        self.assertIsInstance(result, str)

    def test_be_cuda_plugin_property(self):
        """Test that the 'be_cuda_plugin' property returns a string."""
        result = self.api.be_cuda_plugin
        self.assertIsInstance(result, str)

    def test_be_cuda_hashrates_property(self):
        """Test that the 'be_cuda_hashrates' property returns a list."""
        result = self.api.be_cuda_hashrates
        self.assertIsInstance(result, list)

    def test_be_cuda_hashrate_10s_property(self):
        """Test that the 'be_cuda_hashrate_10s' property returns a float or None."""
        result = self.api.be_cuda_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_hashrate_1m_property(self):
        """Test that the 'be_cuda_hashrate_1m' property returns a float or None."""
        result = self.api.be_cuda_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_hashrate_15m_property(self):
        """Test that the 'be_cuda_hashrate_15m' property returns a float or None."""
        result = self.api.be_cuda_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_property(self):
        """Test that the 'be_cuda_threads' property returns a dictionary."""
        result = self.api.be_cuda_threads
        self.assertIsInstance(result, dict)

    def test_be_cuda_threads_index_property(self):
        """Test that the 'be_cuda_threads_index' property returns an integer."""
        result = self.api.be_cuda_threads_index
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_amount_property(self):
        """Test that the 'be_cuda_threads_amount' property returns an integer."""
        result = self.api.be_cuda_threads_amount
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_blocks_property(self):
        """Test that the 'be_cuda_threads_blocks' property returns an integer."""
        result = self.api.be_cuda_threads_blocks
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_bfactor_property(self):
        """Test that the 'be_cuda_threads_bfactor' property returns an integer."""
        result = self.api.be_cuda_threads_bfactor
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_bsleep_property(self):
        """Test that the 'be_cuda_threads_bsleep' property returns an integer."""
        result = self.api.be_cuda_threads_bsleep
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_affinity_property(self):
        """Test that the 'be_cuda_threads_affinity' property returns an integer."""
        result = self.api.be_cuda_threads_affinity
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_dataset_host_property(self):
        """Test that the 'be_cuda_threads_dataset_host' property returns a boolean."""
        result = self.api.be_cuda_threads_dataset_host
        self.assertIsInstance(result, bool)

    def test_be_cuda_threads_hashrates_property(self):
        """Test that the 'be_cuda_threads_hashrates' property returns a list."""
        result = self.api.be_cuda_threads_hashrates
        self.assertIsInstance(result, list)

    def test_be_cuda_threads_hashrate_10s_property(self):
        """Test that the 'be_cuda_threads_hashrate_10s' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_10s
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_hashrate_1m_property(self):
        """Test that the 'be_cuda_threads_hashrate_1m' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_1m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_hashrate_15m_property(self):
        """Test that the 'be_cuda_threads_hashrate_15m' property returns a float or None."""
        result = self.api.be_cuda_threads_hashrate_15m
        self.assertIsInstance(result, (float, type(None)))

    def test_be_cuda_threads_name_property(self):
        """Test that the 'be_cuda_threads_name' property returns a string."""
        result = self.api.be_cuda_threads_name
        self.assertIsInstance(result, str)

    def test_be_cuda_threads_bus_id_property(self):
        """Test that the 'be_cuda_threads_bus_id' property returns a string."""
        result = self.api.be_cuda_threads_bus_id
        self.assertIsInstance(result, str)

    def test_be_cuda_threads_smx_property(self):
        """Test that the 'be_cuda_threads_smx' property returns an integer."""
        result = self.api.be_cuda_threads_smx
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_arch_property(self):
        """Test that the 'be_cuda_threads_arch' property returns an integer."""
        result = self.api.be_cuda_threads_arch
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_global_mem_property(self):
        """Test that the 'be_cuda_threads_global_mem' property returns an integer."""
        result = self.api.be_cuda_threads_global_mem
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_clock_property(self):
        """Test that the 'be_cuda_threads_clock' property returns an integer."""
        result = self.api.be_cuda_threads_clock
        self.assertIsInstance(result, int)

    def test_be_cuda_threads_memory_clock_property(self):
        """Test that the 'be_cuda_threads_memory_clock' property returns an integer."""
        result = self.api.be_cuda_threads_memory_clock
        self.assertIsInstance(result, int)


if __name__ == "__main__":
    unittest.main()
