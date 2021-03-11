from django.contrib.auth.backends import ModelBackend

from researcher_req.models import User, Researcher

from .utils import verify_signature

class ChallengeAuthBackend(ModelBackend):
    """
    Log in to Django with a challenge

    """
    def authenticate(self, request, username=None, is_challenge=False, challenge='', response=''):
        # This would be to avoid that all auth attempts use 
        # this mechanism
        # print('authenticate called')

        if not is_challenge or challenge == '' or response == '':
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        researcher = Researcher.objects.get(user=user)

        # check response is valid signature of challenge
        # with the user's public_key
        if verify_signature(researcher.publickey, challenge, response):
            return user
        
        return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None