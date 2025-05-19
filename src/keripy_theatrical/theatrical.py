import importlib
import pkgutil

import keripy_theatrical.utils as utils

THEATRICAL_PATCH_MARKER = "THEATRICAL_PATCHED"

def is_patched(module):
    return getattr(module, THEATRICAL_PATCH_MARKER, False)

def mark_patched(module):
    setattr(module, THEATRICAL_PATCH_MARKER, True)

def init():
    register_global_error_handler()
    add_tracing(
        namespaces=[
            'keri.app',
            # 'keri.db',
        ],
        namespace_exclude_list=[
            'keri.app.oobiing',
            # 'keri.app.oobiing.Oobiery.scoobiDo',
        ]
    )
    apply_patches()

def apply_patches():

    # Dynamically load all modules from the `patchers` namespace
    package = importlib.import_module('.patchers', __package__)
    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f'.patchers.{module_name}', __package__)
        if hasattr(module, 'apply_patches'):
            if is_patched(module):
                continue

            module.apply_patches()
            mark_patched(module)
        else:
            utils.throw(f"No apply_patches method found for patcher: {module_name}")

def register_global_error_handler():
    import sys

    utils.print_purple("Registering global error handler...")


    # OPTION X)
    ############################################################
    def decorate_and_report(exc_type, exc_value, exc_tb):
        if not hasattr(exc_value, "decorated_by"):
            exc_value.decorated_by = "keripy_theatrical"
        # then print the usual traceback
        utils.print_red("--------------------------------")
        utils.print_red(f"Exc type: {exc_type}")
        utils.print_red(f"Exc value: {exc_value}")
        utils.print_red(f"Exc tb: {exc_tb}")
        utils.print_red("--------------------------------")

        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = decorate_and_report

    return

    # OPTION A)
    ############################################################

    # def decorate_exception(exc_value):
    #     # e.g. monkey-patch a .metadata attribute, or wrap in your own Exception subclass
    #     if not hasattr(exc_value, "decorated_by"):
    #         exc_value.decorated_by = "keripy_theatrical"
    #     return exc_value

    def global_excepthook(exc_type, exc_value, exc_tb):
        # decorate_exception(exc_value)
        utils.print_red("--------------------------------")
        utils.print_red(f"Exc type: {exc_type}")
        utils.print_red(f"Exc value: {exc_value}")
        utils.print_red(f"Exc tb: {exc_tb}")
        utils.print_red("--------------------------------")

        # then print the normal traceback
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    import threading

    def thread_exception_hook(args):
        global_excepthook(args.exc_type, args.exc_value, args.exc_traceback)

    threading.excepthook = thread_exception_hook
    sys.excepthook = global_excepthook

    import asyncio

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(lambda loop, ctx: decorate_exception(ctx.get("exception", Exception())))

    return
    return
    return

    # OPTION B)
    ############################################################
    def trace_exceptions(frame, event, arg):

        if event == "exception":
            exc_type, exc_value, exc_tb = arg
            # decorate in-place
            if not hasattr(exc_value, "decorated_by"):
                exc_value.decorated_by = "keripy_theatrical"


            utils.print_red("--------------------------------")
            utils.print_red(f"Event: {event}")
            utils.print_red(f"Frame: {frame}")
            utils.print_red(f"Arg: {arg}")
            utils.print_red("--------------------------------")


        return trace_exceptions

    sys.settrace(trace_exceptions)


def add_tracing(namespaces=None, namespace_exclude_list=None):

    # @see https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-namespace-packages
    def iter_namespace(ns_pkg):
        import pkgutil

        # Specifying the second argument (prefix) to iter_modules makes the
        # returned name an absolute name instead of a relative one. This allows
        # import_module to work without having to do additional modification to
        # the name.

        # Get all submodules, recursively
        return pkgutil.walk_packages(ns_pkg.__path__, ns_pkg.__name__ + ".")

        # Get all direct submodules
        # return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    for namespace in namespaces:
        discovered_modules = [ name for finder, name, ispkg in iter_namespace(importlib.import_module(namespace)) ]
        # utils.print_purple(str(discovered_modules))

        for module in discovered_modules:
            if module in namespace_exclude_list:
                continue
            add_tracing_to_module(importlib.import_module(module))

def tap(fqn, print_args_before_call=True):
    module, cls_name, method_name = fqn.rsplit('.', 2)
    cls = getattr(importlib.import_module(module), cls_name)
    method = getattr(cls, method_name)

    def tap_generator(gen):
        for item in gen:
            utils.print_red(f"[ => Item: {item}")
            yield item


    def tapper(*args, **kwargs):
        # utils.print_dim(f"[TAP] {cls.__module__}.{cls.__name__}.{method_name} called with args: {args} and kwargs: {kwargs}")

        tap_prefix = f"[TAP] {cls.__module__}.{cls.__name__}.{method_name}"

        if not print_args_before_call:
            result = method(*args, **kwargs)

        utils.print_red(f"{tap_prefix}")
        utils.print_red(f"{tap_prefix} => args: {args}")
        utils.print_red(f"{tap_prefix} => kwargs: {kwargs}")

        if print_args_before_call:
            result = method(*args, **kwargs)

        import types
        if isinstance(result, types.GeneratorType):
            utils.print_red(f"{tap_prefix} => RETURNED GENERATOR ITEMS...")
            return tap_generator(result)
        else:
            utils.print_red(f"{tap_prefix} => RETURNED: {result}")

        return result

    setattr(cls, method_name, tapper)
    return method

def patch(fqn, callback=None, append=False):
    module, cls_name, method_name = fqn.rsplit('.', 2)
    cls = getattr(importlib.import_module(module), cls_name)
    method = getattr(cls, method_name)
    # add_tracing_to_class(cls)

    def cb(*args, **kwargs):
        utils.print_dim(f"[PATCH] {cls.__module__}.{cls.__name__}.{method_name} called with args: {args} and kwargs: {kwargs}")
        if callback:
            callback(*args, **kwargs)
        # else:
        #     utils.print_dim(f"[PATCH] {cls.__module__}.{cls.__name__}.{method_name} called with args: {args} and kwargs: {kwargs}")

    def wrapper(*args, **kwargs):
        if not append:
            cb(*args, **kwargs)
            return method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)
            cb(*args, **kwargs, _result=result)
            return result

    setattr(cls, method_name, wrapper)


def add_tracing_to_module(module, exclude_list=None):
    import inspect
    if exclude_list is None:
        exclude_list = []
    for name, obj in inspect.getmembers(module):

        # Allow for explicit exclusion
        fqcn = f"{module.__name__}.{name}"
        if fqcn in exclude_list:
            continue

        # Only consider classes and functions
        if not inspect.isclass(obj) and not inspect.isfunction(obj):
            continue

        # Only consider objects defined within the module
        if obj.__module__ != module.__name__:
            continue

        add_tracing_to_class(obj)

def add_tracing_to_class(cls):
    for name, attr in list(vars(cls).items()):
        if not callable(attr): # skip non-callables
            continue

        if name.startswith("__"): # skip dunder methods
            continue

        # utils.print_green(f"{cls.__module__}.{cls.__name__}.{name}")

        # wrap the original method
        def make_wrapper(method_name, orig_method):
            def wrapper(*args, **kwargs):
                import inspect
                frame = inspect.currentframe().f_back
                file_name = frame.f_code.co_filename
                line_number = frame.f_lineno
                utils.print_dim(f"[TRACE] {cls.__module__}.{cls.__name__}.{method_name} called with args: {args} and kwargs: {kwargs} from {file_name}:{line_number}")
                return orig_method(*args, **kwargs)
            # preserve introspection hints
            wrapper.__name__ = orig_method.__name__
            wrapper.__doc__  = orig_method.__doc__
            return wrapper

        setattr(cls, name, make_wrapper(name, attr))