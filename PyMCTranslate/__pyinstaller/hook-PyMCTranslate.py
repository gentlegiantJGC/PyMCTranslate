from PyInstaller.utils.hooks import collect_submodules, collect_data_files


hiddenimports = collect_submodules("PyMCTranslate")
datas = collect_data_files(
    "PyMCTranslate", includes=["build_number.json", "min_json/**/*.json.gz"]
)
