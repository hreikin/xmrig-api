"""
XMRig module initializer.

This module provides objects to interact with the XMRig miner API.
"""

from .api import XMRigAPI, XMRigAuthorizationError
from .manager import XMRigManager

__name__ = "xmrig"
__version__ = "0.0.3"
__author__ = "Michael Haslam"
__email__ = "hreikin@gmail.com"
__license__ = "MIT"
__description__ = "This module provides objects to interact with the XMRig miner API."
__url__ = "https://hreikin.co.uk/xmrig-api"


__all__ = ["XMRigAPI", "XMRigManager"]