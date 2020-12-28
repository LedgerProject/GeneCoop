import json
from pathlib import Path
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db import IntegrityError, transaction



TITLE_LENGTH = 200
DESCR_LENGTH = 1000
TOKEN_LENGTH = 2000


def read_table():

    BASE_DIR = Path(__file__).resolve().parent.parent

    file_path = f'{BASE_DIR}/resreq.json'

    print(f'Reading conf file {file_path}')

    with open(file_path, "r") as fp:
        requests = json.loads(fp.read())

    # Operation = apps.get_model('researcher_req', 'Operation')
    # Option = apps.get_model('researcher_req', 'Option')

    for option in Option.objects.all():
        option.delete()

    for operation in Operation.objects.all():
        operation.delete()

    for request in requests:

        with transaction.atomic():
            operation_inst = Operation(
                name=request['name'], description=request['description'], key=request['key'])

            # try:
            operation_inst.save()
            index2 = 0
            for option in request['options']:
                option_inst = Option(
                    operation=operation_inst, text=option['text'], description=option['description'])
                option_inst.save()
                index2 += 1

            # except IntegrityError:
                # inst.delete()

class Operation(models.Model):
    name = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    key = models.IntegerField(default=0, unique=True)

    # @classmethod
    # def create(cls, text, key):
    #     operation = cls(text=text, key=key)
    #     return operation
    
    def __str__(self):
        return self.name

class Option(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    text = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)

    # @classmethod
    # def create(cls, text, key):
    #     option = cls(text=text, key=key)
    #     return option

    def __str__(self):
        return self.text

class Request(models.Model):
    name = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.IntegerField(default=0)
    operations = models.ManyToManyField(Operation, through='Membership')
    token = models.CharField(max_length=TOKEN_LENGTH, default = 0)
    request_sent = models.DateTimeField('date sent', default = datetime(1900,1,1))

    class RequestStatus(models.TextChoices):
        NOTSENT = 'NOT SENT', _('Request has not been sent')
        SENT = 'SENT', _('Request has been sent')
        REPLIED = 'REPLIED', _('Request has been fulfilled')

    status = models.CharField(
        max_length=8,
        choices=RequestStatus.choices,
        default=RequestStatus.NOTSENT,
    )

    def replied(self):
        self.status = self.RequestStatus.REPLIED

    def is_replied(self):
        return self.status == self.RequestStatus.REPLIED

    def __str__(self):
        return self.description

class Membership(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    request = models.ForeignKey(Request, on_delete=models.CASCADE)