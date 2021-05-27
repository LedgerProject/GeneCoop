import logging
import inspect
import requests
import hashlib
from pathlib import Path
import json
import copy
import time
from zenroom import zenroom

logger = logging.getLogger(__name__)
# print(f'Logger {__name__}')


KEY_SEP = '_'
TOKEN_SEP = '_'
OPCODE_LEN = 3


def format_request(prepped, encoding=None):
    # prepped has .method, .path_url, .headers and .body attribute to view the request
    encoding = encoding or requests.utils.get_encoding_from_headers(
        prepped.headers)
    body = prepped.body.decode(encoding) if encoding else '<binary data>'
    headers = '\n'.join(['{}: {}'.format(*hv)
                         for hv in prepped.headers.items()])
    return f"""\
{prepped.method} {prepped.path_url} HTTP/1.1
{headers}

{body}"""


def gen_token(name, description, experiments, token_time=None):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    opconcat = "".join([f"{experiment}".zfill(OPCODE_LEN)
                        for experiment in experiments])
    if token_time == None:
        token_time = time.time()
    prelude = f'{token_time}{TOKEN_SEP}{name}{TOKEN_SEP}{description}{TOKEN_SEP}{opconcat}'.encode()

    hash_object = hashlib.blake2b(prelude, digest_size=5)
    token = hash_object.hexdigest()

    return token, token_time

# def decode_token(token):
#     logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
#     tokens = token.split(TOKEN_SEP)
#     experiments = tokens[2]
#     return tokens[1], [experiments[i:i + OPCODE_LEN] for i in range(0, len(experiments), OPCODE_LEN)]


# def request_to_sign(request):
#     logger.debug(f'Generating request to be signed for: {request}')
#     obj = {}
#     obj['text'] = request.text
#     obj['description'] = request.description
#     obj['user_id'] = request.user_id
#     obj['token'] = request.token
#     obj['experiments'] = []
#     exp_json = json.loads(request.experiments)
#     for experiment in exp_json:
#         obj['experiments'].append(experiment['id'])
#     return json.dumps(obj)


def get_signature(request):
    logger.debug(f'Getting signature for request: {request}')
    return json.loads(request.signature)

######################################################
# Zenroom functionality
######################################################


def generate_random_challenge():
    """
        This function calls zenroom to generate
        a random string to be used as challenge
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
        logger.error(f'Exception in zenroom call: {e}')
        return None

    res_json = json.loads(result.output)

    logger.debug(f"Generated challenge: {res_json['challenge']}")

    return res_json['challenge']


def verify_signature(public_key, message, signature):
    """
        This function calls zenroom to verify
        the signature of a message
    """

    contract = """
    rule check version 1.0.0
    Scenario 'ecdh': verify the signature of a request
    Given I have a 'public key' from 'Signer'
    and I have a 'string' named 'message'
    and I have a 'signature' named 'message.signature'
    When I verify the 'message' has a signature in 'message.signature' by 'Signer'
    Then print 'verification passed' as 'string'
    """

    # data = {
    #     "message": message,
    #     "signature": signature
    # }

    # keys = {
    #     "Signer": {
    #         "public_key": public_key
    #     }

    # }

    data = f'{{"message": {json.dumps(message)}, "message.signature": {signature} }}'

    keys = f'{{"Signer": {{"public_key": "{public_key}" }} }}'

    logger.debug(f'verification data: {data}, keys: {keys}')
    # breakpoint()
    try:
        # result = zenroom.zencode_exec(contract, keys=json.dumps(keys), data=json.dumps(data))
        # breakpoint()
        result = zenroom.zencode_exec(
            contract, keys=keys, data=data, conf='debug=0')
    except Exception as e:
        logger.error(f'Exception in zenroom call: {e}')
        # print(f'Exception in zenroom call: {e}')
        return False

    # result = zenroom.zencode_exec(contract, data=json.dumps(data))

    logger.debug(f'result: {result}')

    if not result.output == '':
        res_json = json.loads(result.output)

        if res_json['output'] == 'verification_passed':
            logger.debug(f'Verification passed')
            return True

    logger.debug(f'Verification NOT passed')
    return False


def verify_signed_vc(public_key, signed_vc):
    """
        This function calls zenroom to verify
        a signed verifiable credential
    """

    contract = """
    Rule check version 1.0.0
    Scenario 'w3c' : verify w3c vc signature
    Scenario 'ecdh' : verify
    Given I have a 'public key' from 'Issuer'
    Given I have a 'verifiable credential' named 'my-vc'
    When I verify the verifiable credential named 'my-vc'
    Then print 'verification passed' as 'string'
    """

    data = f'{{"my-vc": {signed_vc}}}'

    keys = f'{{"Issuer": {{"public_key": "{public_key}" }} }}'

    logger.debug(f'verification data: {data}, keys: {keys}')
    # breakpoint()
    try:
        # result = zenroom.zencode_exec(contract, keys=json.dumps(keys), data=json.dumps(data))
        # breakpoint()
        result = zenroom.zencode_exec(
            contract, keys=keys, data=data, conf='debug=0')
    except Exception as e:
        logger.error(f'Exception in zenroom call: {e}')
        # print(f'Exception in zenroom call: {e}')
        return False

    # result = zenroom.zencode_exec(contract, data=json.dumps(data))

    logger.debug(f'result: {result}')

    if not result.output == '':
        res_json = json.loads(result.output)

        if res_json['output'] == 'verification_passed':
            logger.debug(f'Verification passed')
            return True

    logger.debug(f'Verification NOT passed')
    return False


######################################################
# Classes for the settings read from conf file
######################################################

class baseEntity:
    def __init__(self, name, description, id):
        self.name = name
        self.description = description
        self.id = id

    def __str__(self):
        return self.name


class Procedure(baseEntity):
    def __init__(self, name, description, id):
        super(Procedure, self).__init__(name, description, id)

class Option(baseEntity):
    def __init__(self, name, description, id):
        super(Option, self).__init__(name, description, id)


class Experiment(baseEntity):
    def __init__(self, name, description, id, procedures, required):
        super(Experiment, self).__init__(name, description, id)
        self.procedures = procedures
        self.required = required



class Consent(baseEntity):
    """
        This class represent the shared configuration between GeneCoop
        and any party that wants to use GeneCoop consent.
        The configuration file is in JSON-LD format and based on a project ontology
    """

    def __init__(self, name, description, id, role):
        super(Consent, self).__init__(name, description, id)
        self.experiments = {}
        self.options = {}
        self.role = role

    def __str__(self):
        exp_text = []
        for exp_id in self.experiments.keys():
            experiment = self.experiments[exp_id]
            exp_text.append({
                'id': exp_id,
                'name': experiment.name
            })
        opt_text = []
        for opt_id in self.options.keys():
            option = self.options[opt_id]
            opt_text.append({
                'id': opt_id,
                'name': option.name
            })

        return f"Experiments: {', '.join([str(x) for x in exp_text])}, Options: {', '.join([str(x) for x in opt_text])}"

    def add_experiment_obj(self, experiment):
        self.experiments[experiment.id] = experiment

    def add_option_obj(self, option):
        self.options[option.id] = option

    def get_experiment_obj(self, id):
        if id in self.experiments:
            return self.experiments[id]
        return None

    def get_option_obj(self, id):
        if id in self.options:
            return self.options[id]
        return None

    def is_exp_allowed(self, exp_id, chosen_opt_id):
        exp_obj = self.get_experiment_obj(exp_id)
        if not exp_obj == None:
            for opt_id in self.options.keys():
                if chosen_opt_id == opt_id:
                    opt_obj = self.get_option_obj(opt_id)
                    if opt_obj.id == "genecoop:Yes":
                        return True
        return False

def read_conf(role):
    BASE_DIR = Path(__file__).resolve().parent.parent
    file_path = f'{BASE_DIR}/schema/resreq.jsonld'

    logger.info(f'Reading conf file {file_path} for role {role}')
    descrpt_field = 'researcher_description' if role == 'researcher' else 'donor_description'

    with open(file_path, "r") as fp:
        consent = json.loads(fp.read())
        logger.info(f"Consent label: {consent['rdf:label']}")
        assert(consent['@type'] == 'genecoop:Consent')
        aConsent = Consent(name=consent['rdf:label'], description=consent[f'genecoop:{descrpt_field}'], id=consent['@id'], role=role)

        for experiment in consent['genecoop:has_experiments']:
            procedures = []
            for procedure in experiment["genecoop:has_procedures"]:
                aProcedure = Procedure(name=procedure['rdf:label'],description=procedure[f'genecoop:{descrpt_field}'], id=procedure['@id'])
                procedures.append(aProcedure)

            anExperiment = Experiment(name=experiment['rdf:label'],
                                        description=experiment[f'genecoop:{descrpt_field}'],
                                        procedures=procedures,
                                        required=experiment["genecoop:is_required"],
                                        id=experiment['@id'])

            aConsent.add_experiment_obj(anExperiment)
        
        for option in consent['genecoop:has_options']:
            anOption = Option(name=option['rdf:label'], description=f'genecoop:{descrpt_field}', id=option['@id'])
            aConsent.add_option_obj(anOption)
    
    return aConsent      

class SerializeExperiments:
    """
        This class serialise a JSON structure in the DB field.
        It is used to keep track of what experiments in consent/request
        have been authorized.
    """
    NO_OPT = -1

    def __init__(self, conf):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')

        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        self.experiments = []
        self.entry = {
            'id': -1,
            'chosen_option': self.NO_OPT,
            'reply': ""
        }
        self.conf = conf

    def add_experiment_id(self, id):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for experiment in self.experiments:
            if id == experiment['id']:
                return
        new_entry = copy.deepcopy(self.entry)
        new_entry['id'] = id
        self.experiments.append(new_entry)

    def select_option_id(self, exp_id, opt_id):
        """
        Only set the option if experiment exists
        """
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for exp_entry in self.experiments:
            if exp_id == exp_entry['id']:
                exp_entry['chosen_option'] = opt_id
                return

    def reset_option_id(self, exp_id):
        """
        Only reset the option if experiment exists
        """
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for exp_entry in self.experiments:
            if exp_id == exp_entry['id']:
                exp_entry['chosen_option'] = self.NO_OPT
                return

    def set_reply(self, exp_id, reply):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for experiment in self.experiments:
            if exp_id == experiment['id']:
                experiment['reply'] = reply
                return
        logger.debug(
            f'Return without action from {inspect.currentframe().f_code.co_name}')

    def reset(self):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        logger.debug(
            f'Experiments to reset are: {json.dumps(self.experiments)}')
        self.experiments = []
        logger.debug(
            f'Experiments resetted are: {json.dumps(self.experiments)}')

    def serialize(self):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        return json.dumps(self.experiments)

    def unserialize(self, experiments):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        if experiments == None or experiments == "":
            logger.debug(
                f'Return without action from {inspect.currentframe().f_code.co_name}')
            return []
        # reset experiments
        self.reset()
        exp_json = json.loads(experiments)
        logger.debug(f'Loaded experiments: {json.dumps(exp_json)}')
        for experiment in exp_json:
            self.add_experiment_id(experiment['id'])
            self.select_option_id(
                experiment['id'], experiment['chosen_option'])
            self.set_reply(experiment['id'], experiment['reply'])

######################################################
# Verifiable Credentials functionality
######################################################


VC = {
    "@context": [
        "https://www.w3.org/2018/credentials/v1",
        "http://genecoop.waag.org/credentials/v1",
        {
            "gc_id": "http://genecoop.waag.org/ids/",
            "gc_cons": "http://genecoop.waag.org/consents/",
            "gc_schema": "http://genecoop.waag.org/schema/v1/",
            "gc_cred": "http://genecoop.waag.org/credentials/v1/"
        }
    ],
    # this URL allows to retrieve the document
    "id": "gc_cons:__TOKEN__",

    # Name of the Consent
    "name": "Consent for Eye Melanoma research",

    # Here we add the genecoop consent type
    "type": ["VerifiableCredential", "VerifiableConsent"],

    # The issuer is GeneCoop, but it might not have any signature on this credentials
    "issuer": {
        "id": "gc_id:GeneCoop",
        "name": "GeneCoop Consent Service"
    },

    # the verifier needs to see this date is in the past, this is a validity date
    "issuanceDate": "_DATE_",

    # Is this needed? It can be use for schema-validation in JSON, how does it influence the semantic definition?
    # "credentialSchema": {
    # "id": "https://example.org/examples/degree.json",
    # "type": "JsonSchemaValidator2018"
    # },

    "credentialSubject": {
        "id": "__DNA_DONOR_ID__",
        "gc_cred:consents_to": [],
        "gc_cred:prohibits": [],
        #     {
        #         "name": "Array SNP request + Analysis and interpretation",
        #         "id": "gc_schema:exp_000"
        #     }
    },

    "given_to": {"id": "gc_id:__RESEARCHER_ID__"},

    # We do not use the status as the last consent needs to be retrieved
    # # Use this mechanism for status?
    # "credentialStatus": {
    # "id": "https://example.edu/status/24",
    # "type": "CredentialStatusList2017"
    # },

    # This could be used to enforce some operation for the verifier
    "termsOfUse": [
        {
            "type": "gc_cred:IssuerPolicy",
            "gc_cred:obligation": [
                {
                    "gc_cred:assigner": {"id": "gc_id:GeneCoop"},
                    "gc_cred:assignee": {"id": "gc_cred:AllVerifiers"},
                    "gc_cred:target": {"id": "gc_cons:__TOKEN__"},
                    "gc_cred:action": [{"id": "gc_cred:FetchLatestConsent"}]
                }
            ]
        }
    ]
}

def prepare_vc(token, researcher_id, experiments):
    breakpoint()
    vc_str = json.dumps(VC)
    vc_str = vc_str.replace('_TOKEN_', token)
    # vc_str = vc_str.replace('__DNA_DONOR_ID__', donor_id)
    vc_str = vc_str.replace('__RESEARCHER_ID__', researcher_id)
    vc_json = json.loads(vc_str)
    breakpoint()
