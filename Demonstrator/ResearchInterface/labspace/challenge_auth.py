from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

from .utils import verify_challenge

class ChallengeAuthBackend(ModelBackend):
    """Log in to Django with a challenge

    """
    def authenticate(self, request, username=None, is_challenge=False, challenge='', response=''):
        # This would be to avoid that all auth attempts use 
        # this mechanism
        if not is_challenge or challenge == '' or response == '':
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        public_key = user.password

        verify_challenge(public_key, challenge, response)

        # check response is valid signature of challenge
        # with the user's public_key

        return user

        


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None