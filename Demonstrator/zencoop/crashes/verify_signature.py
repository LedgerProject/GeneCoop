import json
from zenroom import zenroom

def verify_signature():

    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': verify the signature of a request
    Given I have a 'public key' from 'Signer'
    and I have a 'string' named 'message'
    and I have a 'signature' named 'message.signature'
    When I verify the 'message' has a signature in 'message.signature' by 'Signer'
    Then print 'verification passed' as 'string'
    """

    data = '{"message": "9yDO2VAkbs2Dqb8NcAU/deaL9TBzM7K+/jHdGAz/Wqpw/+evNsVlBLsoShFe/k4ZbaPk/K6b8r0ZhkyNTUI6wQ==", "message.signature": {"r":"lvzeTbEUpgcT3lfjqvp7XcWKNX0rLxlPGMGDkYWs52w=","s":"7uAqNP6shbT50k4k56TepoiO/oges6L3koFqg0LQUmI="} }'

    keys = '{"Signer": {"public_key": "BGRO8HAnOMeESESnhekVyrsr0q9tHNtI3X7eYaNoVfr9wzThRuL6E9WVltW1jT6z1IVHXSdophZJkBEuYjfa4qg=" } }'


    try:
        # result = zenroom.zencode_exec(contract, keys=json.dumps(keys), data=json.dumps(data))
        # breakpoint()
        result = zenroom.zencode_exec(
            contract, keys=keys, data=data, conf='debug=0')
    except Exception as e:
        print(f'Exception in zenroom call: {e}')
        return False


    if not result.output == '':
        res_json = json.loads(result.output)

        res_json = json.loads(result.output)
        if type(res_json['output']) == list:
            parsed_res = res_json['output'][0]
        else:
            parsed_res = res_json['output']

        if parsed_res == 'verification_passed':
            print(f'Verification passed')
            return True

    print(f'Verification NOT passed')
    return False

if __name__ == "__main__":
    verify_signature()
