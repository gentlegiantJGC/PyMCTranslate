import logging
import sys
import os
from PyMCTranslate.py3.meta import build_number

log = logging.getLogger("pymctranslate")
log.setLevel(logging.INFO)

_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

os.makedirs("./logs", exist_ok=True)
_log_file = logging.FileHandler("./logs/pymctranslate.log", "w", encoding="utf-8")
if "pymct-debug" in sys.argv:
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

log.info(f"PyMCTranslate Version {build_number}")


def enable_console_log(enable=True):
    if enable:
        _log_console.setLevel(logging.INFO)
    else:
        _log_console.setLevel(logging.CRITICAL)
