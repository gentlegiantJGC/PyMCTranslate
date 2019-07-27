import os
from .py3.data_version_handler import VersionContainer

version_container = VersionContainer(os.path.join(os.path.dirname(__file__), 'mappings'))