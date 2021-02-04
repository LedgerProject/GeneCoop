import base64
import json
import requests

SIGN_URL = 'http://localhost:3000/api/genecoop/sign'

def format_prepped_request(prepped, encoding=None):
    # prepped has .method, .path_url, .headers and .body attribute to view the request
    encoding = encoding or requests.utils.get_encoding_from_headers(prepped.headers)
    body = prepped.body.decode(encoding) if encoding else '<binary data>' 
    headers = '\n'.join(['{}: {}'.format(*hv) for hv in prepped.headers.items()])
    return f"""\
{prepped.method} {prepped.path_url} HTTP/1.1
{headers}

{body}"""

def main(request_path, credentials_path):

    with open(request_path, "r") as fp:
        requestData = fp.read()

    with open(credentials_path, "r") as fp:
        credentials = json.loads(fp.read())

    # Standard Base64 Encoding
    encodedBytes = base64.b64encode(requestData.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")

    data = {

        "message": encodedStr
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
    sign_response = session.post(SIGN_URL, json={"data": data, "keys": keys})

    
    if sign_response.status_code == 200:
        print(sign_response.text)
    else:
        prepped = sign_response.request
        print(f'Error from {SIGN_URL}: {sign_response.status_code}')
        print("Request that was sent:")
        print(format_prepped_request(prepped, 'utf8'))
        


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
