"""Module to help to create tests."""
from unittest.mock import Mock

from kytos.core import Controller
# pylint: disable=unused-import
from kytos.core.common import EntityStatus
from kytos.core.config import KytosConfig
from kytos.core.interface import TAG, UNI, Interface
from kytos.core.link import Link
from kytos.core.switch import Switch

# pylint: disable=unused-import


def get_controller_mock():
    """Return a controller mock."""
    options = KytosConfig().options['daemon']
    controller = Controller(options)
    controller.log = Mock()
    return controller
