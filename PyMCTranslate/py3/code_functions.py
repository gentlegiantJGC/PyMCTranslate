import glob
import os
import importlib

code_functions = {}


for code_file in glob.iglob(os.path.join(os.path.dirname(__file__), '..', 'code_functions', '**', '*.py')):
    code_function_name = os.path.splitext(os.path.basename(code_file))[0]
    code_module = importlib.import_module(code_function_name, 'PyMCTranslate.code_functions')
    assert hasattr(code_module, 'main')
    code_functions[code_function_name] = code_module.main


def run(function_name, inputs):
    assert function_name in code_functions
    return code_functions[function_name](*inputs)
