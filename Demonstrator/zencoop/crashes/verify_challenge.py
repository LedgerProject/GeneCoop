import json
from zenroom import zenroom

def create_keypair():
    contract = """
        rule check version 1.0.0
        Scenario 'ecdh': create a keypair
        Given nothing
        When I create the keypair
        Then print 'keypair'
    """

    try:
        result = zenroom.zencode_exec(contract)
    except Exception as e:
        print(f'Exception in zenroom call: {e}')

    # breakpoint()
    keypair = json.loads(result.output)['keypair']
    print(f'challenge: {keypair}')
    return keypair

def create_challenge():
    """
        Call zenroom to create a random challenge
    """

    contract = """
        rule check version 1.0.0
        Given nothing
        When I create the random object of '512' bits
        and I rename the 'random_object' to 'challenge'
        Then print 'challenge'
    """

    try:
        result = zenroom.zencode_exec(contract)
    except Exception as e:
        print(f'Exception in zenroom call: {e}')

    challenge = json.loads(result.output)['challenge']
    print(f'challenge: {challenge}')
    return challenge

def sign_challenge(public_key, private_key, challenge):
    """
        Sign a challenge with the Signer's credentials
    """
    
    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': create the signature of a challenge
    Given I have a 'string' named 'challenge'
    and I am 'Signer'
    and I have my 'keypair'
    When I create the signature of 'challenge'
    and I rename the 'signature' to 'challenge.signature'
    Then print the 'challenge.signature'
    """
    
    data = {
        "challenge": challenge
    }

    keys = {
        "Signer": {
            "keypair": {
                    "private_key": private_key,
                    "public_key": public_key
                }
        }
    }

    try:
        result = zenroom.zencode_exec(
        contract, keys=json.dumps(keys), data=json.dumps(data))
    except Exception as e:
        print(f'Exception in zenroom call: {e}')
    
    signature = json.loads(result.output)['challenge.signature']
    print(f'signature: {signature}')

    return signature

def verify_challenge(public_key, challenge, signature):
    """
        Call zenroom to verify the signature of a challenge
    """

    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': verify the signature of a request
    Given I have a 'public key' from 'Signer'
    and I have a 'string' named 'challenge'
    and I have a 'signature' named 'signature'
    When I verify the 'challenge' has a signature in 'signature' by 'Signer'
    Then print 'verification passed' as 'string'
    """
    
    data = {
        "challenge": challenge,
        "signature": signature
    }

    keys = {
        "Signer": {
            "public_key": public_key
        }

    }

    try:
        result = zenroom.zencode_exec(
        contract, keys=json.dumps(keys), data=json.dumps(data))
    except Exception as e:
        print(f'Exception in zenroom call: {e}')
    
    verification = json.loads(result.output)['output']

    print(f'verification: {verification}')

    return verification

def main():

    keypair = create_keypair()
    challenge = create_challenge()
    signature = sign_challenge(keypair['public_key'], keypair['private_key'], challenge)
    verification = verify_challenge(keypair['public_key'], challenge, signature)

    assert(verification == "verification_passed")
    

if __name__ == "__main__":
    main()
