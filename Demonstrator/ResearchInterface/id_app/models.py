from django.db import models
from django.contrib.auth.models import AbstractUser

from consent_server.constants import PUBLICKEY_LENGTH, QUESTION_LENGTH, ANSWER_LENGTH

class User(AbstractUser):
    question1 = models.CharField(max_length=QUESTION_LENGTH)
    answer1 = models.CharField(max_length=ANSWER_LENGTH)
    question2 = models.CharField(max_length=QUESTION_LENGTH)
    answer2 = models.CharField(max_length=ANSWER_LENGTH)
    question3 = models.CharField(max_length=QUESTION_LENGTH)
    answer3 = models.CharField(max_length=ANSWER_LENGTH)
    publickey = models.CharField(max_length=PUBLICKEY_LENGTH)

    def assign_qa(self, qas):
        self.answer1 = qas['Answer1.hash']
        self.answer2 = qas['Answer2.hash']
        self.answer3 = qas['Answer3.hash']

        self.question1 = qas['Question1.hash']
        self.question2 = qas['Question2.hash']
        self.question3 = qas['Question3.hash']

    def check_qa(self, qas):
        if not self.answer1 == qas['Answer1.hash']:
            return False
        if not self.answer2 == qas['Answer2.hash']:
            return False
        if not self.answer3 == qas['Answer3.hash']:
            return False
        if not self.question1 == qas['Question1.hash']:
            return False
        if not self.question2 == qas['Question2.hash']:
            return False
        if not self.question3 == qas['Question3.hash']:
            return False
        
        return True
