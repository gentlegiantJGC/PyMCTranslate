import os
import shutil
import glob
from typing import List
from setuptools import setup, find_packages
import versioneer
from wheel.bdist_wheel import bdist_wheel
# from Cython.Build import cythonize


# future possible Cython support
# ext = []
# pyx_path = f"PyMCTranslate/**/*.pyx"
# if next(glob.iglob(pyx_path, recursive=True), None):
#     # This throws an error if it does not match any files
#     ext += cythonize(
#         pyx_path,
#         language_level=3,
#         annotate=True,
#     )

SKIP_MINIFY_IF_EXISTS = False
JSON_MINIFIED = False  # a way to track if the json has been minified so it doesn't get run more than once


def get_paths(path_glob: str) -> List[str]:
    return [
        os.path.relpath(path, "PyMCTranslate")
        for path in glob.glob(path_glob, recursive=True)
    ]


def minify_json(pymct_path: str):
    from minify_json import main as _minify_json
    global JSON_MINIFIED
    if not JSON_MINIFIED:
        json_path = os.path.join(pymct_path, "json")
        min_json_path = os.path.join(pymct_path, "min_json")
        if os.path.isdir(json_path):
            if not SKIP_MINIFY_IF_EXISTS and os.path.isdir(min_json_path):
                shutil.rmtree(min_json_path)

            if not os.path.isdir(min_json_path):
                print("Minifying JSON")
                _minify_json(pymct_path)
        else:
            assert os.path.isdir(
                min_json_path
            ), "Neither the PyMCTranslate/json or PyMCTranslate/min_json directories exists."
        JSON_MINIFIED = True


cmdclass = versioneer.get_cmdclass()


class CmdBDistWheel(bdist_wheel):
    def finalize_options(self):
        minify_json("PyMCTranslate")
        self.distribution.package_data.setdefault("PyMCTranslate", []).extend(
            get_paths(os.path.join("PyMCTranslate", "min_json", "**", "*.json.gz"))
        )
        super().finalize_options()

cmdclass["bdist_wheel"] = CmdBDistWheel


setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    packages=find_packages(exclude=("PyMCTranslate.json",)),
    # ext_modules=ext,
)
