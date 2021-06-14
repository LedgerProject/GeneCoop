import json
from zenroom import zenroom

def verify_signed_vc():
    data = '{"my-vc": {"@context":["https://www.w3.org/2018/credentials/v1","http://genecoop.waag.org/credentials/v1#",{"gc_cred":"http://genecoop.waag.org/credentials/v1#","gc_docs":"https://genecoop.waag.org/docs/","gc_ids":"https://genecoop.waag.org/ids/","gc_schema":"http://genecoop.waag.org/schema/v1#"}],"credentialSubject":{"gc_cred:consents_to":[{"id":"gc_schema:exp_000","name":"Array SNP request + Analysis and interpretation"},{"id":"gc_schema:exp_001","name":"Copy Number Variation"},{"id":"gc_schema:exp_003","name":"Population study. DNA data available for secondary use"}],"gc_cred:prohibits":[{"id":"gc_schema:exp_002","name":"SNP Variant detection (Biomarker or Pathogenic)"}],"id":"https://genecoop.waag.org/ids/superduper"},"given_to":{"id":"https://genecoop.waag.org/ids/researcherA"},"id":"gc_docs:3e424387d2","issuanceDate":"2021-06-07T14:09:17.162Z","issuer":{"id":"gc_ids:GeneCoop","name":"GeneCoop Consent Service"},"name":"Consent for Eye Melanoma research","proof":{"jws":"eyJhbGciOiJFUzI1NksiLCJiNjQiOnRydWUsImNyaXQiOiJiNjQifQ..LeL430a4rG39VUECHePk1RjejevSGZtn97iqeoT3glmSTX2qZr0X1O07h-Gg7X1DgYW-pR17idDVTGsXsaVG1Q","proofPurpose":"authenticate","type":"Zenroom","verificationMethod":"https://genecoop.waag.org/ids/superduper"},"termsOfUse":[{"gc_cred:obligation":[{"gc_cred:action":[{"id":"gc_cred:FetchLatestConsent"}],"gc_cred:assignee":{"id":"gc_cred:AllVerifiers"},"gc_cred:assigner":{"id":"gc_ids:GeneCoop"},"gc_cred:target":{"id":"gc_docs:3e424387d2"}}],"type":"gc_cred:IssuerPolicy"}],"type":["VerifiableCredential","VerifiableConsent"]}}'

    keys = '{"Issuer": {"public_key": "BCPyi2O0McdRkkfB6+DbXfz7Wiv7UmX9+rYiQCUBov6ZVu/kE0PZMThgAowU/E0F8xsRnAE/QeBGR4/yEtnlj/8=" } }'

    contract = """
        Rule check version 1.0.0
        Scenario 'w3c' : verify w3c vc signature
        Scenario 'ecdh' : verify
        Given I have a 'public key' from 'Issuer'
        Given I have a 'verifiable credential' named 'my-vc'
        When I verify the verifiable credential named 'my-vc'
        Then print 'verification passed' as 'string'
        """



    try:
        # result = zenroom.zencode_exec(contract, keys=json.dumps(keys), data=json.dumps(data))
        # breakpoint()
        result = zenroom.zencode_exec(
            contract, keys=keys, data=data, conf='debug=0')
    except Exception as e:
        print(f'Exception in zenroom call: {e}')
        # print(f'Exception in zenroom call: {e}')
        return False

    # result = zenroom.zencode_exec(contract, data=json.dumps(data))

    print(f'result: {result}')

    if not result.output == '':
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
    verify_signed_vc()
