import logging
import sys
import os
from PyMCTranslate import version

log = logging.getLogger('pymctranslate')

_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.makedirs('./logs', exist_ok=True)
_log_file = logging.FileHandler('./logs/pymctranslate.log', 'w')
if 'pymct-debug' in sys.argv:
    _log_file.setLevel(logging.DEBUG)
else:
    _log_file.setLevel(logging.INFO)
_log_file.setFormatter(_formatter)
log.addHandler(_log_file)

_log_console = logging.StreamHandler()
_log_console.setLevel(logging.WARN)
_log_console.setFormatter(_formatter)
log.addHandler(_log_console)

# TODO: find a proper way to implement this
log.info(f'PyMCTranslate Version 0.{version}')
