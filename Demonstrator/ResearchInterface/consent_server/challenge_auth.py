from django.contrib.auth.backends import ModelBackend

from researcher_app.models import User, Researcher

from .utils import verify_signature

class ChallengeAuthBackend(ModelBackend):
    """
    Log in to Django with a challenge

    """
    def authenticate(self, request, is_researcher, username=None, challenge='', response=''):
        # This would be to avoid that all auth attempts use 
        # this mechanism
        # print('authenticate called')

        if challenge == '' or response == '':
            return None
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
        if is_researcher:
            researcher = Researcher.objects.get(user=user)
            publickey = researcher.publickey
        else:
            publickey = username

        # check response is valid signature of challenge
        # with the user's public_key
        if verify_signature(publickey, challenge, response):
            return user
        
        return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None