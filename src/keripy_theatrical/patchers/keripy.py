import importlib
import json

from keripy_theatrical.utils import log, print_blue, print_green, print_purple, print_cyan, print_red, print_dim, dump_caller, dump_call_stack, dump


REQUEST_DUMP_MAX_BODY_LEN = 150
DUMP_FULL_CALL_STACK = True

def apply_patches():
    print_purple("Applying patches")
    monkey_patch_http_stream_messenger()

    # monkey_patch_witness_publisher()
    # monkey_patch_notifier()
    # monkey_patch_poster()

    instrumented_modules = [
        'keri.app.agenting',
        'keri.app.notifying',
        'keri.app.forwarding',
    ]

    for module in instrumented_modules:
        add_tracing_to_module(importlib.import_module(module))

    # patch('keri.app.agenting.HTTPMessenger.responseDo')
    # patch('keri.app.agenting.HTTPMessenger.responseDo', append=False, callback=lambda self, *args, **kwargs: (
    #     dump_caller(),
    #     dump_call_stack(),
    # ))

def patch(fqn, callback=None, append=False):
    module, cls_name, method_name = fqn.rsplit('.', 2)
    cls = getattr(importlib.import_module(module), cls_name)
    method = getattr(cls, method_name)
    # add_tracing_to_class(cls)

    def cb(*args, **kwargs):
        if callback:
            callback(*args, **kwargs)
        else:
            print_dim(f"[PATCH] {cls.__module__}.{cls.__name__}.{method_name} called with args: {args} and kwargs: {kwargs}")

    def wrapper(*args, **kwargs):
        if not append:
            cb(*args, **kwargs)
            return method(*args, **kwargs)
        else:
            result = method(*args, **kwargs)
            cb(*args, **kwargs)
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

        # print_green(f"{cls.__module__}.{cls.__name__}.{name}")

        # wrap the original method
        def make_wrapper(method_name, orig_method):
            def wrapper(*args, **kwargs):
                print_dim(f"[TRACE] {cls.__module__}.{cls.__name__}.{method_name} called")
                return orig_method(*args, **kwargs)
            # preserve introspection hints
            wrapper.__name__ = orig_method.__name__
            wrapper.__doc__  = orig_method.__doc__
            return wrapper

        setattr(cls, name, make_wrapper(name, attr))

# def monkey_patch_notifier():
#     from keri.app.notifying import Notifier

#     _orig_init = Notifier.__init__

#     def patched_init(self, *args, **kwargs):
#         print_purple("Notifier.__init__")
#         return _orig_init(self, *args, **kwargs)

#     Notifier.__init__ = patched_init

# def monkey_patch_poster():
#     from keri.app.forwarding import Poster

#     _orig_init = Poster.__init__

#     def patched_init(self, *args, **kwargs):
#         print_purple("Poster.__init__")
#         return _orig_init(self, *args, **kwargs)

#     Poster.__init__ = patched_init

# def monkey_patch_witness_publisher():
#     from keri.app.agenting import WitnessPublisher

#     _orig_init = WitnessPublisher.__init__

#     def patched_init(self, *args, **kwargs):
#         print_purple("WitnessPublisher.__init__")
#         return _orig_init(self, *args, **kwargs)

#     WitnessPublisher.__init__ = patched_init

def monkey_patch_http_stream_messenger():
    from keri.app.agenting import HTTPStreamMessenger

    _orig_recur = HTTPStreamMessenger.recur

    def patched_recur(self, tyme, deeds=None):
        if self.client.responses:

            # Build the raw request message.
            raw_request = self.client.requester.build()

            # Peek next response.
            # After dumping, we will hand over to the original recur() method
            # which will pop the response from the list.
            response = self.client.attrify(self.client.responses[0])

            print_blue("~~~~~~~~~~~~~~~~~ HTTP Request -> Response ~~~~~~~~~~~~~~~~~")

            dump_hio_request(raw_request)
            log('', prefix='| ')
            dump_hio_response(response)

            log()
            if DUMP_FULL_CALL_STACK:
                dump_call_stack()
            log()

        return _orig_recur(self, tyme, deeds)

    HTTPStreamMessenger.recur = patched_recur

def dump_hio_request(raw_request):

    # Extract request line, headers and body
    preamble, body = raw_request.split(b'\r\n\r\n', 1)
    request_line, headers = preamble.split(b'\r\n', 1)

    # Headers as dict
    headers_dict = {}
    for header in headers.split(b'\r\n'):
        key, value = header.split(b': ', 1)
        headers_dict[key.decode('utf-8')] = value.decode('utf-8')

    # Truncate body
    body_decoded = body.decode('utf-8')
    body_decoded = body_decoded if len(body_decoded) <= REQUEST_DUMP_MAX_BODY_LEN else body_decoded[:REQUEST_DUMP_MAX_BODY_LEN] + '...'

    # Print request line, headers and body
    print_green(request_line.decode('utf-8'), prefix='| ')
    print_blue("Request Headers: ", prefix='| ')
    log(json.dumps(headers_dict, indent=4), prefix='| ')
    log('', prefix='| ')
    print_blue("Body: ", prefix='| ', end='')
    log(body_decoded)

def dump_hio_response(response):
    print_blue('Response', prefix='| ')
    response_data = {
        'Status': f'{response.status} {response.reason}',
        'Headers': {k: v for k, v in response.headers.items()},
        'Body': response.body.decode('utf-8'),
    }
    log(json.dumps(response_data, indent=4), prefix='| ')
