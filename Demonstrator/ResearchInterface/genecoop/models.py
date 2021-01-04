import json, copy
from os import name
from pathlib import Path
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db import IntegrityError, transaction

TITLE_LENGTH = 200
DESCR_LENGTH = 1000
TOKEN_LENGTH = 2000
OPERATIONS_LENGTH = 1000 
KEY_SEP='_'

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
    
    def addOption(self, option_key):
        self.options.append(option_key)

    def getOptions(self):
        return self.options

class Option(baseEntity):
    def __init__(self, text, description, key):
        super(Option,self).__init__( text, description, key )
        self.operation = -1

    def setOperation(self, operation_key):
        self.operation = operation_key

class Config:
    def __init__(self):
        self.operations = {}
        self.options = {}

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

class SerializeOperations:
    def __init__(self):
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

    def addOperation(self, key):
        for operation in self.operations:
            if key == operation['key']:
                return
        new_entry = copy.deepcopy(self.entry)
        new_entry['key'] = key
        self.operations.append(new_entry)

    def addOption(self, ope_key, opt_key):
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        return
                    ope_entry['options'].append({
                        'key' : opt_key
                    })
        
    def selectOption(self, ope_key, opt_key):
        """
        Only set the option if operation and option exist
        """
        for ope_entry in self.operations:
            if ope_key == ope_entry['key']:
                for opt_entry in ope_entry['options']:
                    if opt_key == opt_entry['key']:
                        ope_entry['chosen_option'] = opt_key
                        return
                    
        

    def serializeOperations(self):
        return json.dumps(self.operations)

    def unserializeOperations(self, operations):
        # print(f"Operation {operations}")
        if operations == None or operations == "":
            return []
        ope_json = json.loads(operations)
        for operation in ope_json:
            self.addOperation(operation['key'])
            for option in operation['options']:
                self.addOption(operation['key'], option['key'])
            self.selectOption(operation['key'], operation['chosen_option'])



    



def read_conf():

    BASE_DIR = Path(__file__).resolve().parent.parent

    file_path = f'{BASE_DIR}/resreq.json'

    print(f'Reading conf file {file_path}')

    with open(file_path, "r") as fp:
        operations = json.loads(fp.read())
        
        myConfig = Config()

    for operation in operations:
        anOperation = Operation(text=operation['user']['text'], description=operation['user']['description'], key=f"{operation['key']}".zfill(4))
        myConfig.add_operation(anOperation)

        for option in operation['options']:
            opt_key = f"{option['key']}".zfill(4)
            option_key = f"{anOperation.key}{KEY_SEP}{opt_key}"
            anOption = Option(text=option['text'], description=option['user']['description'], key=option_key)
            anOption.setOperation(anOperation.key)
            anOperation.addOption(anOption.key)
            myConfig.add_option(anOption)

    return myConfig


class Consent(models.Model):
    text = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.IntegerField(default=0)
    operations = models.CharField(max_length=OPERATIONS_LENGTH, default="")
    token = models.CharField(primary_key=True, max_length=TOKEN_LENGTH, default="")
    request_approved = models.DateTimeField('date signed', default = datetime(1900,1,1))

    class RequestStatus(models.TextChoices):
        NOTDONE = 'NOT DONE', _('Consent has not been signed yet')
        DONE = 'DONE', _('Consent has been signed')

    status = models.CharField(
        max_length=8,
        choices=RequestStatus.choices,
        default=RequestStatus.NOTDONE,
    )

    def __str__(self):
        return self.description

    def is_signed(self):
        return self.status == self.RequestStatus.DONE

    def sign(self):
        self.request_approved = datetime.now()
        self.status = self.RequestStatus.DONE
    

# class Membership(models.Model):
#     operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
#     consent = models.ForeignKey(Consent, on_delete=models.CASCADE)