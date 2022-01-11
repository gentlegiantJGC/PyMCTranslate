import glob
import os.path
import re
from PyInstaller.utils.hooks import get_package_paths
import pkgutil
import PyMCTranslate.code_functions


hiddenimports = [
    name
    for _, name, _ in pkgutil.walk_packages(
        PyMCTranslate.code_functions.__path__,
        PyMCTranslate.code_functions.__name__ + ".",
    )
]


def get_glob_files(g):
    """Get all files matching the given glob."""
    return [p for p in glob.glob(g, recursive=True) if os.path.isfile(p)]


def collect_data_files(package, excludes=()):
    """
    The function that comes with pyinstaller takes a long time.

    :param package: The package name to find files in.
    :param excludes: A list of regexes to exclude.
    :return: A list of files.
    """
    root, package_path = get_package_paths(package)
    # get all files
    d = get_glob_files(os.path.join(package_path, "**", "*"))
    # remove the files that match the regexes
    for ex in excludes:
        match = re.compile(ex)
        d = [p for p in d if not match.fullmatch(p)]
    return [(p, os.path.dirname(os.path.relpath(p, root))) for p in d]


datas = collect_data_files(
    "PyMCTranslate",
    excludes=[
        r"^.+\.(py[cod]?|dll|so|dylib|log|md)$",
        re.escape(os.sep).join([".*PyMCTranslate", "json", r".*\.json"]),
    ],
)
print("datas", datas[-5:])
