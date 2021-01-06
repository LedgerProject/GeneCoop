from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.db import models

from labspace.constants import TITLE_LENGTH, DESCR_LENGTH, OPERATIONS_LENGTH, TOKEN_LENGTH, USERID_LENGTH


class Consent(models.Model):
    text = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.CharField(max_length=USERID_LENGTH, default="")
    operations = models.CharField(max_length=OPERATIONS_LENGTH, default="")
    token = models.CharField(primary_key=True, max_length=TOKEN_LENGTH, default="")
    request_received = models.DateTimeField('date received', default = datetime(1900,1,1))
    request_signed = models.DateTimeField('date signed', default = datetime(1900,1,1))

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
        self.request_signed = datetime.now()
        self.status = self.RequestStatus.DONE
    
    def unsign(self):
        self.request_signed = datetime(1900,1,1)
        self.status = self.RequestStatus.NOTDONE
    
