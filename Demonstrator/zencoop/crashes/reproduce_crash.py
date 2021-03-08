"""Zenroom bindings for python 3.6+"""

import io
import json
import ctypes as ct
from dataclasses import dataclass, field

import fnmatch
import pathlib
import os

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
import os
import sys



_CURRENT_SOURCE_PATH = pathlib.Path(__file__).parent.resolve()

# parent_dir = _CURRENT_SOURCE_PATH.parent.resolve()

LIBZENROOM_LOC = os.path.join(_CURRENT_SOURCE_PATH, fnmatch.filter(
                    os.listdir(_CURRENT_SOURCE_PATH), "*.so")[0])


_LIBZENROOM = ct.CDLL(str(LIBZENROOM_LOC))

@contextmanager
def redirect_sys_stream(is_stdout, stream):
    fd_to_redirect = sys.stdout.fileno() if is_stdout else sys.stderr.fileno()
    saved_fd = os.dup(fd_to_redirect)
    with NamedTemporaryFile() as write_buf:
        os.dup2(write_buf.fileno(), fd_to_redirect)
        try:
            yield
        finally:
            write_buf.flush()
            with open(write_buf.name, 'rb') as read_buf:
                stream.write(read_buf.read())
            os.close(fd_to_redirect)
            os.dup2(saved_fd, fd_to_redirect)
            os.close(saved_fd)

@dataclass
class ZenResult():
    output: str = field()
    error: str = field()

    def __post_init__(self):
        try:
            self.result = json.loads(self.output)
        except json.JSONDecodeError:
            self.result = None


def _char_p(x):
    return ct.c_char_p(None if x is None else x.encode())


def _apply_call(call, script, conf, keys, data):
    outbuf = io.BytesIO()
    errbuf = io.BytesIO()
    with redirect_sys_stream(True, outbuf), redirect_sys_stream(False, errbuf):
        call(
            _char_p(script),
            _char_p(conf),
            _char_p(keys),
            _char_p(data)
        )
    return ZenResult(
        outbuf.getvalue().decode().strip(),
        errbuf.getvalue().decode().strip(),
    )


def zenroom_exec(script, conf=None, keys=None, data=None):
    return _apply_call(_LIBZENROOM.zenroom_exec, script, conf, keys, data)


def zencode_exec(script, conf=None, keys=None, data=None):
    return _apply_call(_LIBZENROOM.zencode_exec, script, conf, keys, data)

SCRIPT = '''
Scenario 'ecdh': Decrypt the message with the password
Given that I have a valid 'secret message'
Given that I have a 'string' named 'password'
When I decrypt the text of 'secret message' with 'password'
When I rename the 'text' to 'textDecrypted'
Then print the 'textDecrypted' as 'string'
'''

KEYS = '''
{
    "password": "myVerySecretPassword"
}
'''

DATA = '''
{
    "secret_message": {
        "checksum": "76U+nWVZBwBMbOOktCnZug==",
        "header": "QSB2ZXJ5IGltcG9ydGFudCBzZWNyZXQ=",
        "iv": "R+B2z2pTLkMVGFCuFHnYL5sAIeuolYmgUOdMm2AOvTI=",
        "text": "Df8C8Kkd+ngVAi/tGUe905VPTwId4hv+iL31dgylkDaDumI3BpRO5bN1qKfSsBi2KOA="
    }
}
'''

res = zencode_exec(SCRIPT, None, KEYS, DATA)
print(res.result["textDecrypted"])
print(res.error)

res = zencode_exec(SCRIPT, None, KEYS, DATA)
print(res.result["textDecrypted"])
print(res.error)

script = """
        rule check version 1.0.0
        Given nothing
        When I create the random object of '512' bits
        and I rename the 'random_object' to 'challenge'
        Then print 'challenge'
    """

# result = zencode_exec(script, conf='debug=0')
# result = zencode_exec(script)

# print(result)

script = """
        rule check version 1.0.0
        Scenario 'ecdh': verify the signature of a request
        Given I have a 'public key' from 'Researcher'
        and I have a 'string' named 'challenge'
        and I have a 'signature' named 'response'
        When I verify the 'challenge' has a signature in 'response' by 'Researcher'
        Then print 'verification passed' as 'string'
    """

data = {
        "challenge": "SqF+zwzz2KXrwr9ZbMep56/8FexuXjroQwsnHW73bUc4/ffKfOlFOXsXUol97GNh40RxtKmWhCq1F9koK4NLnA==",
        "response": {
            "r": "CEOKU4azUdA+s/EZKdhNlTCFX1rk6d5268w297buE+I=",
            "s": "hJb/O0EiK7QKo83x57VXOszvPOPSuXWb/1IHBgAvKPs="
        }
    }

keys = {
        "Researcher": {
            "public_key": "BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg="
        }

    }

# result = zencode_exec(script, keys=json.dumps(keys), data=json.dumps(data), conf='debug=0')
# result = zencode_exec(script, keys=json.dumps(keys), data=json.dumps(data))

# print(result)