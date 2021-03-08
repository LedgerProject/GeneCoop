from datetime import datetime
from django.utils import timezone
import pytz
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser

from labspace.constants import TITLE_LENGTH, DESCR_LENGTH, OPERATIONS_LENGTH, TOKEN_LENGTH, USERID_LENGTH, KEY_LENGTH, SIGNATURE_LENGTH



class User(AbstractUser):
    pass

class Researcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=DESCR_LENGTH)
    institute = models.CharField(max_length=TITLE_LENGTH)
    publickey = models.CharField(max_length=KEY_LENGTH)
    # private_key = models.CharField(max_length=KEY_LENGTH)
    institute_publickey = models.CharField(max_length=KEY_LENGTH)


class Request(models.Model):
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE)
    text = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.CharField(max_length=USERID_LENGTH, default="")
    operations = models.CharField(max_length=OPERATIONS_LENGTH, default="")
    token = models.CharField(max_length=TOKEN_LENGTH, unique=True)
    signature = models.CharField(max_length=SIGNATURE_LENGTH, default="")
    request_sent = models.DateTimeField(
        'date sent', default=timezone.make_aware(datetime(1900, 1, 1)))
    request_checked = models.DateTimeField(
        'date signed', default=timezone.make_aware(datetime(1900, 1, 1)))

    class RequestStatus(models.TextChoices):
        NOTSENT = 'NOT SENT', _('Request has not been sent')
        SENT = 'SENT', _('Request has been sent')
        NOTREPLIED = 'NOT REPLIED', _('Request has not been replied')
        REPLIED = 'REPLIED', _('Request has been replied')

    status = models.CharField(
        max_length=15,
        choices=RequestStatus.choices,
        default=RequestStatus.NOTSENT,
    )

    def replied(self):
        self.request_checked = timezone.now()
        self.status = self.RequestStatus.REPLIED

    def not_replied(self):
        self.request_checked = timezone.now()
        self.status = self.RequestStatus.NOTREPLIED

    def is_replied(self):
        return self.status == self.RequestStatus.REPLIED

    def __str__(self):
        return self.description
