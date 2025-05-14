import keripy_theatrical.utils as utils

THEATRICAL_PATCH_MARKER = "THEATRICAL_PATCHED"

def is_patched(module):
    return getattr(module, THEATRICAL_PATCH_MARKER, False)

def mark_patched(module):
    setattr(module, THEATRICAL_PATCH_MARKER, True)

def apply_patches():
    import importlib
    import pkgutil

    register_global_error_handler()

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