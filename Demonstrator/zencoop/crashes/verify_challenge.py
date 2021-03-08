import json
from zenroom import zenroom

def _verify_challenge():
    """
        This function calls zenroom to generate a random object
    """

    contract = """
        rule check version 1.0.0
        Given nothing
        When I create the random object of '512' bits
        and I rename the 'random_object' to 'challenge'
        Then print 'challenge'
    """

    try:
        result = zenroom.zencode_exec(contract, conf='debug=0')
    except Exception as e:
        print(f'Exception in zenroom call: {e}')


    print(f'result: {result}')


def verify_challenge(public_key, challenge, response):
    """
        This function calls zenroom to verify
        the signature of a challenge

        parameters are not used at the moment to reduce source of problems
    """

    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': verify the signature of a request
    Given I have a 'public key' from 'Researcher'
    and I have a 'string' named 'challenge'
    and I have a 'signature' named 'response'
    When I verify the 'challenge' has a signature in 'response' by 'Researcher'
    Then print 'verification passed' as 'string'
    """
    
    data = {
        "challenge": "hPNnxTr/It/fpy7Hv+4osrD8JN8riCsJbGrErZWwByrjSpBWWbkbrK1+ZJo/5K0Ok6FVSUTldjEvRYG15hNwSw==",
        "response": {"r":"t1ZwCfJEoH39TCuAVuGzgTQ9XY1ZQlvFp8d0201E+d8=","s":"AuLyBAo2wySg8atLkbNyJAKDU2QxXLTw6hHUfl58584="}
    }

    keys = {
        "Researcher": {
            "public_key": "BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg="
        }

    }

    # data = {
    #     "challenge": "SqF+zwzz2KXrwr9ZbMep56/8FexuXjroQwsnHW73bUc4/ffKfOlFOXsXUol97GNh40RxtKmWhCq1F9koK4NLnA==",
    #     "response": {
    #         "r": "CEOKU4azUdA+s/EZKdhNlTCFX1rk6d5268w297buE+I=",
    #         "s": "hJb/O0EiK7QKo83x57VXOszvPOPSuXWb/1IHBgAvKPs="
    #     }
    # }

    # keys = {
    #     "Researcher": {
    #         "public_key": "BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg="
    #     }

    # }

    print(f'verification data: {json.dumps(data)}, keys: {json.dumps(keys)}')

    # breakpoint()
    result = zenroom.zencode_exec(
        contract, keys=json.dumps(keys), data=json.dumps(data), conf='debug=0')

    print(f'result: {result}')


def main():

    public_key = 'BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg='
    challenge = '9WXzrRJ1Yhr5wXH/Rqoztflak9JjXyPJCc5V4hT9CLWN3BeuHEkemi4IfCd+lLHKpwiHOUpsIqHrSAKdJNGrsg=='
    response = {"r": "6rdTSqxyeL/PivuPCyupxWbqjgRh/s2y12NM/Bzetb4=",
                "s": "D0SRtbdFFkAyidRlD5+HpdgP6Bji2BUYW5m0YNyhKvc="}

    _verify_challenge()
    verify_challenge(public_key, challenge, response)
    


if __name__ == "__main__":
    main()
