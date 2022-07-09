from setuptools import setup
import versioneer

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
    cmdclass=versioneer.get_cmdclass(),
    # ext_modules=ext,
)
