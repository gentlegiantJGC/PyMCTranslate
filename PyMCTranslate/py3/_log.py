import logging
import sys
from PyMCTranslate.py3.meta import build_number

"""
By default the logger only logs to the console.
If you wish to modify the handlers you should
1) Get the logger
2) Remove and close all existing handlers
3) Set up the logger how you desire

Step 2 may not be required if you set up the logger before this module is imported
but there is no harm in doing it and if you don't everything may get logged to the console twice.
"""


def _init_logging():
    main_log = logging.getLogger("PyMCTranslate")
    if not main_log.handlers:
        # if no handlers have been bound then set up a default one
        main_log.setLevel(logging.DEBUG if "amulet-debug" in sys.argv else logging.INFO)

        formatter = logging.Formatter("%(levelname)s - %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        main_log.addHandler(console_handler)


_init_logging()

log = logging.getLogger(__name__)
log.info(f"PyMCTranslate Version {build_number}")
