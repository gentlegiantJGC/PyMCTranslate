import os
import shutil
import glob
from typing import List
from setuptools import setup, Extension, find_packages
import versioneer
import minify_json

try:
    from wheel.bdist_wheel import bdist_wheel
except ImportError:
    bdist_wheel = False

# future possible Cython support
ext_modules = []
try:
    from Cython.Build import cythonize
except ImportError:
    CYTHON_COMPILE = False
else:
    extensions = [
        Extension(
            name="PyMCTranslate.py3.api.version.translate", sources=["PyMCTranslate/py3/api/version/translate.pyx"]
        )
    ]
    if os.path.exists(os.path.join(".", extensions[0].sources[0])):
        ext_modules = cythonize(extensions, language_level=3, annotate=True)

# read the requirements from the requirements.txt file
with open(os.path.join(".", "requirements.txt")) as requirements_fp:
    requirements = [
        line for line in requirements_fp.readlines() if not line.startswith("git+")
    ]

JSON_MINIFIED = False  # a way to track if the json has been minified so it doesn't get run more than once


def get_json_files(json_glob: str) -> List[str]:
    return [
        os.path.relpath(path, "PyMCTranslate") for path in
        glob.glob(
            json_glob,
            recursive=True
        )
    ]


cmdclass = versioneer.get_cmdclass()


# command for source distribution
class CmdSDist(cmdclass["sdist"]):
    def finalize_options(self):
        self.distribution.package_data["PyMCTranslate"] += get_json_files(
            os.path.join("PyMCTranslate", "json", "**", "*.json")
        )
        self.distribution.data_files = [
            (
                "",
                [
                    "LICENSE",
                    "minify_json.py",
                    "README.md",
                    "requirements.txt",
                    "versioneer.py"
                ]
            )
        ]
        super().finalize_options()


cmdclass["sdist"] = CmdSDist

if bdist_wheel:
    class CmdBDist(bdist_wheel):
        def finalize_options(self):
            global JSON_MINIFIED
            if not JSON_MINIFIED:
                if os.path.isdir(os.path.join("PyMCTranslate", "json")):
                    if os.path.isdir(os.path.join("PyMCTranslate", "min_json")):
                        shutil.rmtree(os.path.join("PyMCTranslate", "min_json"))
                    self.announce("Minifying JSON. This may take a while.")
                    minify_json.main("PyMCTranslate")
                else:
                    assert os.path.isdir(os.path.join("PyMCTranslate", "min_json")), "Neither the PyMCTranslate/json or PyMCTranslate/min_json directories exists."
                JSON_MINIFIED = True
            self.distribution.package_data["PyMCTranslate"] += get_json_files(
                os.path.join("PyMCTranslate", "min_json", "**", "*.json.gz")
            )
            super().finalize_options()


    cmdclass["bdist_wheel"] = CmdBDist

setup(
    name="PyMCTranslate",
    version=versioneer.get_version(),
    description="A Minecraft data translation system.",
    author="James Clare",
    author_email="amuleteditor@gmail.com",
    install_requires=requirements,
    packages=find_packages(),
    package_data={
        "PyMCTranslate": [
            "build_number",
            os.path.join("code_functions", "*.py")
        ]
    },
    cmdclass=cmdclass,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
