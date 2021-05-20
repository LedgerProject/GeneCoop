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
#         obj['experiments'].append(experiment['key'])
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


######################################################
# Classes for the settings read from conf file
######################################################

class baseEntity:
    def __init__(self, name, description, key):
        self.name = name
        self.description = description
        self.key = key

    def __str__(self):
        return self.name


class Experiment(baseEntity):
    def __init__(self, name, description, key, procedures, required):
        super(Experiment, self).__init__(name, description, key)
        self.procedures = procedures
        self.required = required
        self.options = []

    def add_option_key(self, option_key):
        self.options.append(option_key)

    def get_option_keys(self):
        return self.options


class Option(baseEntity):
    def __init__(self, name, description, key):
        super(Option, self).__init__(name, description, key)
        self.experiment = -1

    def set_exp_key(self, experiment_key):
        self.experiment = experiment_key


class ConsentConfig:
    """
        This class represent the shared configuration between GeneCoop
        and any party that wants to use GeneCoop consent.
        The configuration file is in JSON-LD format and based on a project ontology
    """

    def __init__(self, role):
        self.experiments = {}
        self.options = {}
        BASE_DIR = Path(__file__).resolve().parent.parent
        self.file_path = f'{BASE_DIR}/resreq.jsonld'
        self.role = role

    def __str__(self):
        exp_text = []
        for exp_key in self.experiments.keys():
            experiment = self.experiments[exp_key]
            opt_text = []
            for opt_key in experiment.get_option_keys():
                opt_text.append({
                    'key': opt_key
                })

            ', '.join([str(x) for x in opt_text])
            exp_text.append({
                'key': exp_key,
                'name': experiment.name,
                'options': opt_text
            })
        return ', '.join([str(x) for x in exp_text])

    def add_experiment_obj(self, experiment):
        self.experiments[experiment.key] = experiment

    def add_option_obj(self, option):
        self.options[option.key] = option

    def get_experiment_obj(self, key):
        if key in self.experiments:
            return self.experiments[key]
        return None

    def get_option_obj(self, key):
        if key in self.options:
            return self.options[key]
        return None

    def is_exp_allowed(self, exp_key, allowed_opt_key):
        exp_obj = self.get_experiment_obj(exp_key)
        if not exp_obj == None:
            for opt_key in exp_obj.get_option_keys():
                if allowed_opt_key == opt_key:
                    opt_obj = self.get_option_obj(opt_key)
                    if opt_obj.name == "Yes":
                        return True
        return False

    def read_conf(self):

        logger.info(f'Reading conf file {self.file_path} for role {self.role}')
        descrpt_field = 'researcher_description' if self.role == 'researcher' else 'donor_description'

        with open(self.file_path, "r") as fp:
            consent = json.loads(fp.read())
            logger.info(f"Consent label: {consent['rdf:label']}")
            assert(consent['@type'] == 'genecoop:Consent')

            for experiment in consent['genecoop:has_experiments']:
                anExperiment = Experiment(name=experiment['rdf:label'],
                                        description=experiment[f'genecoop:{descrpt_field}'],
                                        procedures=[procedure[f'genecoop:{descrpt_field}'] for procedure in experiment['genecoop:has_procedures']],
                                        required=(experiment["genecoop:is_required"]),
                                        key=f"{experiment['genecoop:has_key']}".zfill(OPCODE_LEN))

                for option in experiment['genecoop:has_options']:
                    tmp_key = f"{option['genecoop:has_key']}".zfill(OPCODE_LEN)
                    option_key = f"{anExperiment.key}{KEY_SEP}{tmp_key}"
                    anOption = Option(
                        name=option['rdf:label'], description=f'genecoop:{descrpt_field}', key=option_key)
                    anOption.set_exp_key(anExperiment.key)
                    anExperiment.add_option_key(anOption.key)
                    self.add_option_obj(anOption)

                self.add_experiment_obj(anExperiment)


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
            'key': -1,
            'chosen_option': self.NO_OPT,
            'options': [
                # {
                #     'key' : -1
                # }
            ],
            'reply': ""
        }
        self.conf = conf

    def add_experiment_key(self, key):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for experiment in self.experiments:
            if key == experiment['key']:
                return
        new_entry = copy.deepcopy(self.entry)
        new_entry['key'] = key
        self.experiments.append(new_entry)

        # Process options
        experiment = self.conf.get_experiment_obj(key)
        for opt_key in experiment.get_option_keys():
            self.__add_option_key__(key, opt_key)

    def __add_option_key__(self, exp_key, opt_key):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for exp_entry in self.experiments:
            if exp_key == exp_entry['key']:
                for opt_entry in exp_entry['options']:
                    if opt_key == opt_entry['key']:
                        logger.debug(
                            f"Experiment {exp_key} has already option {opt_key}")
                        return
                exp_entry['options'].append({
                    'key': opt_key
                })
                logger.debug(
                    f"Adding to experiment: {exp_key} option {opt_key}")
                logger.debug(
                    f"Options for experiment: {exp_key} are: {json.dumps(exp_entry['options'])}")
                return
        logger.debug(
            f"Return with no action for experiment {exp_key}, option {opt_key}")

    def select_option_key(self, exp_key, opt_key):
        """
        Only set the option if experiment and option exist
        """
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for exp_entry in self.experiments:
            if exp_key == exp_entry['key']:
                for opt_entry in exp_entry['options']:
                    if opt_key == opt_entry['key']:
                        exp_entry['chosen_option'] = opt_key
                        return
    
    def reset_option_key(self, exp_key):
        """
        Only reset the option if experiment exists
        """
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for exp_entry in self.experiments:
            if exp_key == exp_entry['key']:
                exp_entry['chosen_option'] = self.NO_OPT
                return

    def set_reply(self, exp_key, reply):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for experiment in self.experiments:
            if exp_key == experiment['key']:
                experiment['reply'] = reply
                return
        logger.debug(
            f'Return without action from {inspect.currentframe().f_code.co_name}')

    def reset(self):
        logger.debug(
            f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        logger.debug(f'Experiments to reset are: {json.dumps(self.experiments)}')
        self.experiments = []
        logger.debug(f'Experiments resetted are: {json.dumps(self.experiments)}')

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
            self.add_experiment_key(experiment['key'])
            self.select_option_key(
                experiment['key'], experiment['chosen_option'])
            self.set_reply(experiment['key'], experiment['reply'])
