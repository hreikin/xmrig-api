import unittest
from xmrig.exceptions import XMRigAPIError, XMRigAuthorizationError, XMRigConnectionError, XMRigDatabaseError, XMRigManagerError

class TestXMRigExceptions(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
