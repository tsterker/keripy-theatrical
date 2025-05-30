import importlib
import json

from keripy_theatrical.utils import log, print_blue, print_green, print_purple, print_cyan, print_red, print_dim, dump_caller, dump_call_stack, dump

REQUEST_DUMP_MAX_BODY_LEN = 150
DUMP_FULL_CALL_STACK = True

def apply_patches():
    print_purple("Applying patches")
    monkey_patch_http_stream_messenger()

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