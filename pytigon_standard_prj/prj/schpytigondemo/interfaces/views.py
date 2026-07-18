from django.conf import settings

from pytigon_lib.schviews.viewtools import dict_to_template


import os


from pytigon_lib.schtools import nim_ext

ext_path = os.path.join(settings.DATA_PATH, settings.PRJ_NAME, "prjlib")

try:
    lib = nim_ext.load_nim_lib(os.path.join(ext_path, "schpytigondemo_test_nim"), "ext")
except Exception:
    lib = None


def make_csum_fun():
    from pytigon_lib.schtools.llvm_exec import compile_str_to_module, get_function
    from ctypes import CFUNCTYPE, c_int

    fun_str = """
    define dso_local i32 @cadd(i32 %0, i32 %1) #0 {
      %3 = alloca i32, align 4
      %4 = alloca i32, align 4
      store i32 %0, i32* %3, align 4
      store i32 %1, i32* %4, align 4
      %5 = load i32, i32* %3, align 4
      %6 = load i32, i32* %4, align 4
      %7 = add nsw i32 %5, %6
      ret i32 %7
    }
    """

    compile_str_to_module(fun_str)
    func_ptr = get_function("cadd")
    cfunc = CFUNCTYPE(c_int, c_int, c_int)(func_ptr)
    return cfunc


try:
    csum = make_csum_fun()
except Exception:
    csum = None


@dict_to_template("interfaces/v_test_interfaces.html")
def test_interfaces(request, **argv):
    """
    Test various native extension interfaces and return results.

    Executes WASM (via wasmtime), Nim native extensions, nimext Python
    bindings, and LLVM assembly JIT-compiled functions, collecting the
    output of each test into a list of (label, result) tuples rendered
    via the interfaces/v_test_interfaces.html template.
    """

    results = []

    title1 = "wasm from zig"
    import interfaces.applib

    try:
        from wasmtime import Store, Module, Instance

        wasm_path = os.path.join(interfaces.applib.__path__[0], "test_zig.wasm")
        store = Store()
        module = Module.from_file(store.engine, wasm_path)
        instance = Instance(store, module, [])
        sum_func = instance.exports(store)["add"]
        result1 = sum_func(store, 2, 2)
    except Exception:
        result1 = "wasmtime not available"

    results.append((title1, result1))

    title2 = "json_test"
    try:
        result2 = nim_ext.ext.json_test(x=100, y=300, value="Hello world!")
    except Exception:
        result2 = "nim ext error"
    results.append((title2, result2))

    title3 = "int_test"
    try:
        result3 = nim_ext.ext.int_test(10)
    except Exception:
        result3 = "nim ext error"
    results.append((title3, result3))

    title4 = "float_test"
    try:
        result4 = nim_ext.ext.float_test(100.0)
    except Exception:
        result4 = "nim ext error"
    results.append((title4, result4))

    title5 = "string_test"
    try:
        result5 = nim_ext.ext.string_test(b"Hello")
    except Exception:
        result5 = "nim ext error"
    results.append((title5, result5))

    title6 = "string_test_from_utf"
    try:
        result6 = nim_ext.ext.string_test_str("Hello")
    except Exception:
        result6 = "nim ext error"
    results.append((title6, result6))

    title7 = "void_test"
    try:
        result7 = nim_ext.ext.void_test()
    except Exception:
        result7 = "nim ext error"
    results.append((title7, result7))

    title8 = "string_int_test"
    try:
        result8 = nim_ext.ext.string_int_test("string int test")
    except Exception:
        result8 = "nim ext error"
    results.append((title8, result8))

    title9 = "json_test2"
    try:
        result9 = nim_ext.ext.json_test2()
    except Exception:
        result9 = "nim ext error"
    results.append((title9, result9))

    import nimext

    title10 = "nimext test"
    try:
        result10 = nimext.greet("world") + " from nimext"
    except Exception:
        result10 = "nimext error"
    results.append((title10, result10))

    title11 = "llvm assembly"
    result11 = csum(2, 2) if csum else "llvm not available"
    results.append((title11, result11))

    return {"object_list": tuple(results)}
