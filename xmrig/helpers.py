"""
XMRig Helpers module.

This module provides helper functions and classes for the XMRig API interactions and operations.
It includes:

- Logging configuration for the XMRig API.
- Custom exception classes for handling specific API errors.
"""

import logging

log = logging.getLogger("XMRigAPI")

class XMRigAPIError(Exception):
    """
    Exception raised when a general error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the API issue.
    """

    def __init__(self, message: str = "An error occurred with the XMRig API.") -> None:
        """
        Initialize the API error.

        Args:
            message (str): Error message. Defaults to a generic API error message.
        """
        self.message = message
        super().__init__(self.message)

class XMRigAuthorizationError(Exception):
    """
    Exception raised when an authorization error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the authorization issue.
    """

    def __init__(self, message: str = "Access token is required but not provided. Please provide a valid access token.") -> None:
        """
        Initialize the authorization error.

        Args:
            message (str): Error message. Defaults to a generic authorization error message.
        """
        self.message = message
        super().__init__(self.message)

class XMRigConnectionError(Exception):
    """
    Exception raised when a connection error occurs with the XMRig API.

    Attributes:
        message (str): Error message explaining the connection issue.
    """

    def __init__(self, message: str = "Failed to connect to the XMRig API. Please check the IP, port, and network connection.") -> None:
        """
        Initialize the connection error.

        Args:
            message (str): Error message. Defaults to a generic connection error message.
        """
        self.message = message
        super().__init__(self.message)