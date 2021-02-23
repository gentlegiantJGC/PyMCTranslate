from PyInstaller.utils.hooks import collect_data_files
import pkgutil
import PyMCTranslate.code_functions

hiddenimports = [
    name for _, name, _ in pkgutil.walk_packages(PyMCTranslate.code_functions.__path__, PyMCTranslate.code_functions.__name__ + ".")
]

datas = collect_data_files("PyMCTranslate", excludes=["__pyinstaller"])
