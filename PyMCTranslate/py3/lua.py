import glob
import os
from lupa import LuaRuntime
lua = LuaRuntime()

lua_functions = {}

for lua_file in glob.iglob(os.path.join(os.path.dirname(__file__), '..', 'lua', '**', '*.lua')):
    lua_function_name = os.path.basename(lua_file)[:-4]
    with open(lua_file) as l:
        lua_functions[lua_function_name] = lua.eval(l.read())


def run(function_name, inputs):
    assert function_name in lua_functions
    return lua_functions[function_name](*inputs)
