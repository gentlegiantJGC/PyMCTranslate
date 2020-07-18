import glob
import os
import importlib.util

code_functions = {}


for code_file in glob.iglob(
    os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "code_functions", "**", "*.py"
    ),
    recursive=True,
):
    code_function_name = os.path.splitext(os.path.basename(code_file))[0]

    spec = importlib.util.spec_from_file_location(code_function_name, code_file,)
    code_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(code_module)

    assert hasattr(code_module, "main")
    code_functions[code_function_name] = code_module.main


def run(function_name, inputs):
    assert (
        function_name in code_functions
    ), f"Function {function_name} could not be found"
    return code_functions[function_name](*inputs)
