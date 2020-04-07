import logging
import sys
import os
from PyMCTranslate import version

log = logging.getLogger('pymctranslate')
log.setLevel(logging.INFO)

_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

os.makedirs('./logs', exist_ok=True)
_log_file = logging.FileHandler('./logs/pymctranslate.log', 'w')
if 'pymct-debug' in sys.argv:
    _log_file.setLevel(logging.DEBUG)
    log.setLevel(logging.DEBUG)
else:
    _log_file.setLevel(logging.INFO)
_log_file.setFormatter(_formatter)
log.addHandler(_log_file)

_log_console = logging.StreamHandler()
_log_console.setLevel(logging.WARNING)
_log_console.setFormatter(_formatter)
log.addHandler(_log_console)

# TODO: find a proper way to implement this
log.info(f'PyMCTranslate Version 0.{version}')


def enable_console_log(enable=True):
    if enable:
        _log_console.setLevel(logging.INFO)
    else:
        _log_console.setLevel(logging.CRITICAL)
