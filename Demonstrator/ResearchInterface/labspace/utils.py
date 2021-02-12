import logging
import inspect
import requests
from pathlib import Path
import json, copy

logger = logging.getLogger(__name__)
# print(f'Logger {__name__}')


KEY_SEP='_'
TOKEN_SEP='_'

def format_request(prepped, encoding=None):
    # prepped has .method, .path_url, .headers and .body attribute to view the request
    encoding = encoding or requests.utils.get_encoding_from_headers(prepped.headers)
    body = prepped.body.decode(encoding) if encoding else '<binary data>' 
    headers = '\n'.join(['{}: {}'.format(*hv) for hv in prepped.headers.items()])
    return f"""\
{prepped.method} {prepped.path_url} HTTP/1.1
{headers}

{body}"""


def gen_token(user_id, operations):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    opconcat = TOKEN_SEP.join([f"{operation['key']}".zfill(4) for operation in operations])
    token = f'{user_id}{TOKEN_SEP}{opconcat}'
    return token

def decode_token(token):
    logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
    tokens = token.split('_')
    return tokens[0], tokens[1:]

def request_to_sign(request):
    logger.debug(f'Generating request to be signed for: {request}')
    obj = {}
    obj['text'] = request.text
    obj['description'] = request.description
    obj['user_id'] = request.user_id
    obj['token'] = request.token
    obj['operations'] = []
    ope_json = json.loads(request.operations) 
    for operation in ope_json:
        obj['operations'].append(operation['key'])
    return json.dumps(obj)

def get_signature(request):
    logger.debug(f'Getting signature for request: {request}')
    return json.loads(request.signature)

class baseEntity:
    def __init__(self, text, description, key):
        self.text = text
        self.description = description
        self.key = key

    def __str__(self):
        return self.text


class Operation(baseEntity):
    def __init__(self, text, description, key, statements, permissions, required):
        super(Operation,self).__init__( text, description, key )
        self.statements = statements 
        self.permissions = permissions
        self.required = required
        self.options = []
    
    def add_option_key(self, option_key):
        self.options.append(option_key)

    def get_option_keys(self):
        return self.options

class Option(baseEntity):
    def __init__(self, text, description, key):
        super(Option,self).__init__( text, description, key )
        self.operation = -1

    def set_operation_key(self, operation_key):
        self.operation = operation_key

class ConsentConfig:
    """
        This class represent the shared configuration between GeneCoop
        and any party that wants to use GeneCoop consent.
        At the moment the conf file is just a json file
    """
    def __init__(self, role):
        self.operations = {}
        self.options = {}
        BASE_DIR = Path(__file__).resolve().parent.parent
        self.file_path = f'{BASE_DIR}/resreq.json'
        self.role = role
        

    def __str__(self):
        ope_text = []
        for ope_key in self.operations.keys():
            operation = self.operations[ope_key]
            opt_text = []
            for opt_key in operation.get_option_keys():
                opt_text.append({
                    'key' : opt_key
                })

            ', '.join([str(x) for x in opt_text])
            ope_text.append({
                'key' : ope_key,
                'text' : operation.text,
                'options' : opt_text
            })
        return ', '.join([str(x) for x in ope_text])

    def add_operation_obj(self, operation):
        self.operations[operation.key] = operation

    def add_option_obj(self, option):
        self.options[option.key] = option

    def get_operation_obj(self, key):
        if key in self.operations:
            return self.operations[key]
        return None

    def get_option_obj(self, key):
        if key in self.options:
            return self.options[key]
        return None

    def is_op_allowed(self, ope_key, allowed_opt_key):
        ope_obj = self.get_operation_obj(ope_key)
        if not ope_obj == None:
            for opt_key in ope_obj.get_option_keys():
                if allowed_opt_key == opt_key:
                    opt_obj = self.get_option_obj(opt_key)
                    if opt_obj.text == "yes":
                        return True
        return False

    def read_conf(self):

        print(f'Reading conf file {self.file_path} for role {self.role}')

        with open(self.file_path, "r") as fp:
            operations = json.loads(fp.read())

            for operation in operations:
                anOperation = Operation(text=operation[self.role]['text'], 
                                        description=operation[self.role]['description'], 
                                        statements=operation['statements'], 
                                        permissions=operation['permissions'],
                                        required=(operation['required']),
                                        key=f"{operation['key']}".zfill(4))

                for option in operation['options']:
                    opt_key = f"{option['key']}".zfill(4)
                    option_key = f"{anOperation.key}{KEY_SEP}{opt_key}"
                    anOption = Option(text=option['text'], description=option[self.role]['description'], key=option_key)
                    anOption.set_operation_key(anOperation.key)
                    anOperation.add_option_key(anOption.key)
                    self.add_option_obj(anOption)
                
                self.add_operation_obj(anOperation)


class SerializeOperations:
    """
        This class serialise a JSON structure in the DB field.
        It is used to keep track of what operations in consent/request
        have been authorized.
    """
    def __init__(self, conf):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        self.operations = []
        self.entry = {
            'key' : -1,
            'chosen_option' : -1,
            'options' : [
                # {
                #     'key' : -1
                # }
            ],
            'reply' : ""
        }
        self.conf = conf

    def add_operation_key(self, key):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for operation in self.operations:
            if key == operation['key']:
                return
        new_entry = copy.deepcopy(self.entry)
        new_entry['key'] = key
        self.operations.append(new_entry)

        # Process options
        operation = self.conf.get_operation_obj(key)
        for opt_key in operation.get_option_keys():
            self.__add_option_key__(key, opt_key)

    def __add_option_key__(self, ope_key, opt_key):
        # logger.debug(f'Call to {inspect.currentframe().f_code.co_name}')
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        logger.debug(f"Operation {ope_key} has already option {opt_key}")
                        return
                ope_entry['options'].append({
                    'key' : opt_key
                })
                logger.debug(f"Adding to operation: {ope_key} option {opt_key}")
                logger.debug(f"Options for operation: {ope_key} are: {json.dumps(ope_entry['options'])}")
                return
        logger.debug(f"Return with no action for operation {ope_key}, option {opt_key}")
        
    def select_option_key(self, ope_key, opt_key):
        """
        Only set the option if operation and option exist
        """
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        ope_entry['chosen_option'] = opt_key
                        return
                    

    def set_reply(self, ope_key, reply):
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        for operation in self.operations:
            if ope_key == operation['key']:
                operation['reply'] = reply
                return
        logger.debug(f'Return without action from {inspect.currentframe().f_code.co_name}')


    def reset(self):
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        logger.debug(f'Operations to reset are: {json.dumps(self.operations)}')
        self.operations = []
        logger.debug(f'Operations resetted are: {json.dumps(self.operations)}')


    def serialize(self):
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        return json.dumps(self.operations)

    def unserialize(self, operations):
        logger.debug(f'Called from {inspect.currentframe().f_back.f_code.co_name}')
        if operations == None or operations == "":
            logger.debug(f'Return without action from {inspect.currentframe().f_code.co_name}')
            return []
        # reset operations
        self.reset()
        ope_json = json.loads(operations)
        logger.debug(f'Loaded operations: {json.dumps(ope_json)}')
        for operation in ope_json:
            self.add_operation_key(operation['key'])
            self.select_option_key(operation['key'], operation['chosen_option'])
            self.set_reply(operation['key'], operation['reply'])


    



