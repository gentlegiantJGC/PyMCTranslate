from setuptools import setup
import versioneer
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "build_tools"))

import minify_json

cmdclass=versioneer.get_cmdclass()

minify_json.register(cmdclass)


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


setup(
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    # ext_modules=ext,
)
