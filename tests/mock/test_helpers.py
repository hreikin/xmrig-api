import unittest
from xmrig.helpers import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError, XMRigDatabaseError, XMRigManagerError, XMRigPropertiesError

class TestXMRigHelpers(unittest.TestCase):

    def test_XMRigAPIError(self):
        with self.assertRaises(XMRigAPIError):
            raise XMRigAPIError("API error occurred")

    def test_XMRigAuthorizationError(self):
        with self.assertRaises(XMRigAuthorizationError):
            raise XMRigAuthorizationError("Authorization error occurred")

    def test_XMRigConnectionError(self):
        with self.assertRaises(XMRigConnectionError):
            raise XMRigConnectionError("Connection error occurred")

    def test_XMRigDatabaseError(self):
        with self.assertRaises(XMRigDatabaseError):
            raise XMRigDatabaseError("Database error occurred")

    def test_XMRigManagerError(self):
        with self.assertRaises(XMRigManagerError):
            raise XMRigManagerError("Manager error occurred")

    def test_XMRigPropertiesError(self):
        with self.assertRaises(XMRigPropertiesError):
            raise XMRigPropertiesError("Properties error occurred")

if __name__ == '__main__':
    unittest.main()
