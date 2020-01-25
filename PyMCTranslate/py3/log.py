import sys

# TODO: look into using the proper logging module to do this

log_level = 1  # 0 for no logs, 1 or higher for warnings, 2 or higher for info, 3 or higher for debug
if 'pymct-debug' in sys.argv:
    log_level = 3
elif 'pymct-info' in sys.argv:
    log_level = 2


def debug(msg: str):
    if log_level >= 3:
        print(msg)


def info(msg: str):
    if log_level >= 2:
        print(msg)


def warn(msg: str):
    if log_level >= 1:
        print(msg)