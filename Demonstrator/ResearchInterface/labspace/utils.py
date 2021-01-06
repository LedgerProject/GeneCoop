
from pathlib import Path
import json, copy

KEY_SEP='_'
TOKEN_SEP='_'

class baseEntity:
    def __init__(self, text, description, key):
        self.text = text
        self.description = description
        self.key = key

    def __str__(self):
        return self.text


class Operation(baseEntity):
    def __init__(self, text, description, key):
        super(Operation,self).__init__( text, description, key )
        self.options = []
    
    def add_option(self, option_key):
        self.options.append(option_key)

    def getOptions(self):
        return self.options

class Option(baseEntity):
    def __init__(self, text, description, key):
        super(Option,self).__init__( text, description, key )
        self.operation = -1

    def setOperation(self, operation_key):
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
            for opt_key in operation.getOptions():
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

    def add_operation(self, operation):
        self.operations[operation.key] = operation

    def add_option(self, option):
        self.options[option.key] = option

    def get_operation(self, key):
        if key in self.operations:
            return self.operations[key]
        return None

    def get_option(self, key):
        if key in self.options:
            return self.options[key]
        return None

    def read_conf(self):

        print(f'Reading conf file {self.file_path} for role {self.role}')

        with open(self.file_path, "r") as fp:
            operations = json.loads(fp.read())

            for operation in operations:
                anOperation = Operation(text=operation[self.role]['text'], description=operation[self.role]['description'], key=f"{operation['key']}".zfill(4))

                for option in operation['options']:
                    opt_key = f"{option['key']}".zfill(4)
                    option_key = f"{anOperation.key}{KEY_SEP}{opt_key}"
                    anOption = Option(text=option['text'], description=option[self.role]['description'], key=option_key)
                    anOption.setOperation(anOperation.key)
                    anOperation.add_option(anOption.key)
                    self.add_option(anOption)
                
                self.add_operation(anOperation)


class SerializeOperations:
    """
        This class serialise a JSON structure in the DB field.
        It is used to keep track of what operations in consent/request
        have been authorized.
    """
    def __init__(self, conf):
        self.operations = []
        self.entry = {
            'key' : -1,
            'chosen_option' : -1,
            'options' : [
                {
                    'key' : -1
                }
            ]
        }
        self.conf = conf

    def add_operation(self, key):
        for operation in self.operations:
            if key == operation['key']:
                return
        new_entry = copy.deepcopy(self.entry)
        new_entry['key'] = key
        self.operations.append(new_entry)

        # Process options
        operation = self.conf.get_operation(key)
        for opt_key in operation.getOptions():
            self.__add_option__(key, opt_key)

    def __add_option__(self, ope_key, opt_key):
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        return
                    ope_entry['options'].append({
                        'key' : opt_key
                    })
        
    def select_option(self, ope_key, opt_key):
        """
        Only set the option if operation and option exist
        """
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        ope_entry['chosen_option'] = opt_key
                        return
                    
        

    def serialize(self):
        return json.dumps(self.operations)

    def unserialize(self, operations):
        # print(f"Operation {operations}")
        if operations == None or operations == "":
            return []
        # reset operations
        self.operations = []
        ope_json = json.loads(operations)
        for operation in ope_json:
            self.add_operation(operation['key'])
            for option in operation['options']:
                self.__add_option__(operation['key'], option['key'])
            self.select_option(operation['key'], operation['chosen_option'])



    
def gen_token(user_id, operations):
    opconcat = TOKEN_SEP.join([f"{operation['key']}".zfill(4) for operation in operations])
    token = f'{user_id}{TOKEN_SEP}{opconcat}'
    return token

def decode_token(token):
    tokens = token.split('_')
    return tokens[0], tokens[1:]



