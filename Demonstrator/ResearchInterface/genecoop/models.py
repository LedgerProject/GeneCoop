from datetime import datetime
from django.utils import timezone
import pytz
from django.utils.translation import gettext_lazy as _
from django.db import models

from labspace.constants import TITLE_LENGTH, DESCR_LENGTH, OPERATIONS_LENGTH, TOKEN_LENGTH, USERID_LENGTH, TYPE_LENGTH, LOGMESSAGE_LENGTH
import labspace.utils as labut

class Consent(models.Model):
    text = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.CharField(max_length=USERID_LENGTH, default="")
    operations = models.CharField(max_length=OPERATIONS_LENGTH, default="")
    token = models.CharField(primary_key=True, max_length=TOKEN_LENGTH)
    request_received = models.DateTimeField('date received', default = timezone.make_aware(datetime(1900,1,1)))
    request_signed = models.DateTimeField('date signed', default = timezone.make_aware(datetime(1900,1,1)))

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
        self.request_signed = timezone.now()
        self.status = self.RequestStatus.DONE
    
    def unsign(self):
        self.request_signed = timezone.make_aware(datetime(1900,1,1))
        self.status = self.RequestStatus.NOTDONE
    

class ConsentLogger(models.Model):
    consent = models.ForeignKey(Consent, on_delete=models.CASCADE)
    message = models.CharField(max_length=LOGMESSAGE_LENGTH)
    user_id = models.CharField(max_length=USERID_LENGTH, default="")
    operations = models.CharField(max_length=OPERATIONS_LENGTH, default="")
    token = models.CharField(max_length=TOKEN_LENGTH)
    request_received = models.DateTimeField('date received', default = timezone.make_aware(datetime(1900,1,1)))


    class LogTypes(models.TextChoices):
        IS_SIGNED = 'IS SIGNED?', _('Request to check whether consent is signed')
        ALLOWED_OPERATIONS = 'ALLOWED OPERATIONS', _('Request to check what operations are allowed')
        LOG_OPERATION = 'LOG OPERATION', _('Request to log operation')
        LOG_NOTSIGNEDOPERATION  = 'LOG NOT SIGNED OPERATION', _('Request to log operation which is not signed')

    type = models.CharField(
        max_length=TYPE_LENGTH,
        choices=LogTypes.choices,
        default="",
    )

    def __str__(self):
        return self.message    

    def __handle_token__(self, token):
        self.token = token
        consent = Consent.objects.get(token=self.token)
        assert(consent != None)
        self.request_received = timezone.now()
        self.user_id,  self.operations = labut.decode_token(token)
        return consent


    def log_is_signed(self, token):
        consent = self.__handle_token__(token)
        self.type = self.LogTypes.IS_SIGNED
        self.message = f"Request received to check whether consent is signed for token: {token}, answer is: {consent.is_signed()}"
        

    def log_allowed_operations(self, token, op_results):
        consent = self.__handle_token__(token)
        self.type = self.LogTypes.ALLOWED_OPERATIONS
        msg = [ f"(operation: {op['key']}, option: {op['chosen_option']})" for op in op_results]
        self.message = f"Request received to check what operations are allowed, results is {msg}"
        

    def log_operation(self, token, ope_key, is_allowed):
        consent = self.__handle_token__(token)
        self.type = self.LogTypes.LOG_OPERATION
        self.message = f'Log operation {ope_key}, which is {"" if is_allowed else "NOT"} allowed'
        
    
    def log_not_signed_operation(self, token, ope_key):
        consent = self.__handle_token__(token)
        self.type = self.LogTypes.LOG_NOTSIGNEDOPERATION
        self.message = f'Request to log operation {ope_key}, which is not signed'
