import os
from setuptools import setup, Extension, find_packages

CYTHON_COMPILE = False
try:
    from Cython.Build import cythonize

    CYTHON_COMPILE = True
except Exception:
    pass

requirements_fp = open(os.path.join(".", "requirements.txt"))
requirements = [
    line for line in requirements_fp.readlines() if not line.startswith("git+")
]
requirements_fp.close()

packages = find_packages(
    include=[
        "*",
        "PyMCTranslate.*",
        "PyMCTranslate.py3.*",
        "PyMCTranslate.py3.api.*",
        "PyMCTranslate.py3.api.amulet_objects.*",
        "PyMCTranslate.py3.api.translation_manager.*",
        "PyMCTranslate.py3.api.version.*",
        "PyMCTranslate.py3.util.*",
    ],
    exclude=[],
)

extensions = [
    Extension(
        name="PyMCTranslate.py3.api.version.translate", sources=["PyMCTranslate/py3/api/version/translate.pyx"]
    )
]

SETUP_PARAMS = {
    "name": "pymctranslate",
    "install_requires": requirements,
    "packages": packages,
    "include_package_data": True,
    "zip_safe": False,
}

if CYTHON_COMPILE and os.path.exists(os.path.join(".", extensions[0].sources[0])):
    SETUP_PARAMS["ext_modules"] = cythonize(extensions, language_level=3, annotate=True)

setup(**SETUP_PARAMS)
