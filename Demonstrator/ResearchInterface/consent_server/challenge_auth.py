from django.contrib.auth.backends import ModelBackend

from id_app.models import User

from .utils import verify_signature

class ChallengeAuthBackend(ModelBackend):
    """
    Log in to Django with a challenge

    """
    def authenticate(self, request, username=None, challenge='', response=''):
        # This would be to avoid that all auth attempts use 
        # this mechanism
        # print('authenticate called')
        
        if challenge == '' or response == '':
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        publickey = user.publickey
        # breakpoint()
        # check response is valid signature of challenge
        # with the user's public_key
        if verify_signature(publickey, challenge, response):
            return user
        
        return None


    def get_user(self, id):
        # breakpoint()
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None