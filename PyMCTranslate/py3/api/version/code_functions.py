import importlib
import pkgutil
import PyMCTranslate
import PyMCTranslate.code_functions

code_functions = {}


def _load_function(module_name: str):
    code_module = importlib.import_module(module_name)
    assert hasattr(code_module, "main")
    code_functions[module_name.split(".")[-1]] = code_module.main


def _load_functions():
    package = PyMCTranslate.code_functions
    package_prefix = package.__name__ + "."

    for _, name, _ in pkgutil.walk_packages(package.__path__, package_prefix):
        _load_function(name)


_load_functions()


def run(function_name, inputs):
    assert (
        function_name in code_functions
    ), f"Function {function_name} could not be found"
    return code_functions[function_name](*inputs)
