from datetime import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from consent_server.constants import TITLE_LENGTH, DESCR_LENGTH, EXPERIMENTS_LENGTH, TOKEN_LENGTH, PUBLICKEY_LENGTH, SIGNATURE_LENGTH
from id_app.models import User

class Researcher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=DESCR_LENGTH)
    institute = models.CharField(max_length=TITLE_LENGTH)
    institute_publickey = models.CharField(max_length=PUBLICKEY_LENGTH)

    def __str__(self):
        return self.user.username


class Request(models.Model):
    researcher = models.ForeignKey(Researcher, on_delete=models.CASCADE)
    name = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    experiments = models.CharField(max_length=EXPERIMENTS_LENGTH, default="")
    token = models.CharField(max_length=TOKEN_LENGTH, unique=True)
    token_time = models.FloatField(default=0)
    token_signature = models.CharField(max_length=SIGNATURE_LENGTH, default="")
    request_created = models.DateTimeField(
        'create date', default=timezone.make_aware(datetime(1900, 1, 1)))
    request_checked = models.DateTimeField(
        'checked date', default=timezone.make_aware(datetime(1900, 1, 1)))

    class RequestStatus(models.TextChoices):
        NOTSENT = 'NOT SENT', _('Request has not been sent')
        NOTREPLIED = 'NOT REPLIED', _('Request has not been replied')
        REPLIED = 'REPLIED', _('Request has been replied')

    status = models.CharField(
        max_length=15,
        choices=RequestStatus.choices,
        default=RequestStatus.NOTSENT,
    )

    def created(self):
        self.request_created = timezone.now()
        self.status = self.RequestStatus.NOTREPLIED

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
