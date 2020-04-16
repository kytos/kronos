"""Module to test the napp kytos/kronos."""
import os
import sys
from pathlib import Path

BASE_ENV = Path(os.environ.get('VIRTUAL_ENV', '/'))

KRONOS_PATH = BASE_ENV / 'var/lib/kytos/napps/..'

sys.path.insert(0, str(KRONOS_PATH))
