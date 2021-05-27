import base64
import json
import requests
from consent_server.constants import SIGN_URL, DO_ENCODING

import consent_server.utils as labut

def main(request_path, credentials_path):

    with open(request_path, "r") as fp:
        requestData = fp.read()

    with open(credentials_path, "r") as fp:
        credentials = json.loads(fp.read())

    if DO_ENCODING:
        # Standard Base64 Encoding
        encodedBytes = base64.b64encode(requestData.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")
    else:
        encodedStr = requestData

    data = {

        "message": encodedStr,
        "Signer": {
            "keypair": {
                "private_key": credentials['private_key'],
                "public_key": credentials['public_key'],
            }
        }
    }
    keys = {
        "Signer": {
            "keypair": {
                "private_key": credentials['private_key'],
                "public_key": credentials['public_key'],
            }
        }

    }

    session = requests.Session()
    sign_response = session.post(SIGN_URL, json={"data": data, "keys": {}})

    # print(f"Request that was sent: {labut.format_request(sign_response.request, 'utf8')}")

    if sign_response.status_code == 200:
        print(sign_response.text)
    else:
        print(f'Error from {SIGN_URL}: {sign_response.status_code}')
        print("Request that was sent:")
        print(labut.format_request(sign_response.request, 'utf8'))
        


if __name__ == "__main__":
    import argparse
    from six import text_type

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'input_file',
        type=text_type,
        help='specifies the path to the request file',
    )
    parser.add_argument(
        '-c', '--credentials',
        dest='credentials',
        type=text_type,
        help='specifies the path to the credentials file',
    )
    args, unknown = parser.parse_known_args()

    try:
        main(
            args.input_file,
            args.credentials,
        )
    except KeyboardInterrupt:
        pass
    finally:
        print("Done\n")
