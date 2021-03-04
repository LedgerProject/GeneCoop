import json
from zenroom import zenroom


def verify_challenge(public_key, challenge, response):
    """
        This function calls zenroom to verify
        the signature of a challenge

        parameters are not used at the moment to reduce source of problems
    """

    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': verify the signature of a request
    # Loading data
    Given I have a 'public key' from 'Researcher'
    and I have a 'string' named 'challenge'
    and I have a 'signature' named 'response'
    # The verification happens here: if the verification would fails, Zenroom would stop and print an error
    When I verify the 'challenge' has a signature in 'response' by 'Researcher'
    
    # Here we're printing the original message along with happy statement of success
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

    print(f'verification data: {public_key}, {challenge}, {response}')

    breakpoint()
    result = zenroom.zencode_exec(
        contract, keys=json.dumps(keys), data=json.dumps(data))

    # result = zenroom.zencode_exec(contract, data=json.dumps(data))

    print(f'verification: {result}')


def main():

    public_key = 'BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg='
    challenge = '9WXzrRJ1Yhr5wXH/Rqoztflak9JjXyPJCc5V4hT9CLWN3BeuHEkemi4IfCd+lLHKpwiHOUpsIqHrSAKdJNGrsg=='
    response = {"r": "6rdTSqxyeL/PivuPCyupxWbqjgRh/s2y12NM/Bzetb4=",
                "s": "D0SRtbdFFkAyidRlD5+HpdgP6Bji2BUYW5m0YNyhKvc="}

    verify_challenge(public_key, challenge, response)


if __name__ == "__main__":
    main()
