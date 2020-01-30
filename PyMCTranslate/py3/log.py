import logging
import sys

log = logging.getLogger('pymctranslate')

_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
