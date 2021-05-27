from datetime import datetime
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser

from consent_server.constants import TITLE_LENGTH, DESCR_LENGTH, EXPERIMENTS_LENGTH, TOKEN_LENGTH, TYPE_LENGTH, LOGMESSAGE_LENGTH, SIGNEDVC_LENGTH, PUBLICKEY_LENGTH

import consent_server.utils as labut


class User(AbstractUser):
    publickey = models.CharField(max_length=PUBLICKEY_LENGTH)


class Consent(models.Model):
    name = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCR_LENGTH)
    user_id = models.CharField(max_length=PUBLICKEY_LENGTH, default="")
    experiments = models.CharField(max_length=EXPERIMENTS_LENGTH, default="")
    token = models.CharField(
        primary_key=True, max_length=TOKEN_LENGTH, unique=True)
    signed_vc = models.CharField(max_length=SIGNEDVC_LENGTH)
    consent_created = models.DateTimeField(
        'date created', default=timezone.make_aware(datetime(1900, 1, 1)))
    consent_signed = models.DateTimeField(
        'date signed', default=timezone.make_aware(datetime(1900, 1, 1)))

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

    def sign(self, signed_vc, public_key):
        self.consent_signed = timezone.now()
        self.status = self.RequestStatus.DONE
        self.signed_vc = signed_vc
        self.user_id = public_key

    def init(self, experiments):
        self.consent_created = timezone.now()
        self.status = self.RequestStatus.NOTDONE
        self.user_id = "not assigned yet"
        self.experiments = experiments

    def unsign(self):
        self.consent_signed = timezone.make_aware(datetime(1900, 1, 1))
        self.status = self.RequestStatus.NOTDONE


class ConsentLogger(models.Model):
    consent = models.ForeignKey(Consent, on_delete=models.CASCADE)
    message = models.CharField(max_length=LOGMESSAGE_LENGTH)
    # user_id = models.CharField(max_length=USERID_LENGTH, default="")
    # experiments = models.CharField(max_length=EXPERIMENTS_LENGTH, default="")
    # token = models.CharField(max_length=TOKEN_LENGTH, unique=True)
    # is_signed = models.BooleanField(default=False)
    request_received = models.DateTimeField(
        'date received', default=timezone.make_aware(datetime(1900, 1, 1)))

    class LogTypes(models.TextChoices):
        IS_SIGNED = 'IS SIGNED?', _(
            'Request to check whether consent is signed')
        ALLOWED_EXPERIMENTS = 'ALLOWED EXPERIMENTS', _(
            'Request to check what experiments are allowed')
        LOG_EXPERIMENT = 'LOG EXPERIMENT', _('Request to log experiment')
        LOG_NOTSIGNEDEXPERIMENT = 'LOG NOT SIGNED EXPERIMENT', _(
            'Request to log experiment which is not signed')

    type = models.CharField(
        max_length=TYPE_LENGTH,
        choices=LogTypes.choices,
        default="",
    )

    def __str__(self):
        return self.message

    def __handle_token__(self, token):
        
        consent = Consent.objects.get(token=token)
        assert(consent != None)
        self.request_received = timezone.now()
        return consent
        # self.token = token
        # self.user_id = consent.user_id
        # self.experiments = consent.experiments
        # self.is_signed = consent.is_signed()

    def log_is_signed(self, token):
        consent = self.__handle_token__(token)
        self.type = self.LogTypes.IS_SIGNED
        self.message = f"Request received to check whether consent is signed for token: {token}, answer is: {consent.is_signed()}"

    def log_allowed_experiments(self, token, exp_results):
        self.__handle_token__(token)
        self.type = self.LogTypes.ALLOWED_EXPERIMENTS
        msg = [
            f"(experiment: {exp['id']}, option: {exp['chosen_option']})" for exp in exp_results]
        self.message = f"Request received to check what experiments are allowed, results is {msg}"

    def log_experiment(self, token, exp_key, is_allowed):
        self.__handle_token__(token)
        self.type = self.LogTypes.LOG_EXPERIMENT
        self.message = f'Log experiment {exp_key}, which is {"" if is_allowed else "NOT"} allowed'

    def log_not_signed_experiment(self, token, exp_key):
        self.__handle_token__(token)
        self.type = self.LogTypes.LOG_NOTSIGNEDEXPERIMENT
        self.message = f'Request to log experiment {exp_key}, which is not signed'
