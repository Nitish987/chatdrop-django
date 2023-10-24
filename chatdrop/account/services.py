import user_agents

from django.conf import settings
from django.core.cache import cache
from utils import otp, generator, security
from utils.platform import Platform
from utils.messenger import Mailer
from .jwt_token import Jwt, EncryptedJwt
from .models import User, PreKeyBundle, ProfilePhoto, ProfileCoverPhoto, GoogleOAuthClientId, WebLoginState
from friends.models import Friend, FriendRequest
from fanfollowing.models import Following, FollowRequest
from privacy.models import BlockedUser
from .exceptions import UserNotFoundError, PreKeyBundleNotFoundError, NoCacheDataError, NoDataError, ProfileError
from django.contrib.auth import authenticate
from firebase_admin.auth import create_custom_token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.utils import timezone
from datetime import timedelta




class UserService:
    '''User Service for user model crud operations'''

    @staticmethod
    def create_user(data) -> User:
        return User.objects.create_user_with_profile(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            gender=data.get('gender'),
            date_of_birth=data.get('date_of_birth'),
            msg_token=data.get('msg_token'),
            email=data.get('email'),
            password=data.get('password'),
        )
    
    @staticmethod
    def get_user(uid) -> User:
        if User.objects.filter(uid=uid).exists():
            return User.objects.get(uid=uid)
        raise UserNotFoundError()
    
    @staticmethod
    def get_user_by_username(username):
        if User.objects.filter(username=username).exists():
            return User.objects.get(username=username)
        raise UserNotFoundError()
    
    
    @staticmethod
    def delete_user(uid):
        if User.objects.filter(uid=uid).exists():
            User.objects.get(uid=uid).delete()
        raise UserNotFoundError()


    @staticmethod
    def update_fcm_token(user, token=''):
        user.msg_token = token
        user.save()
    
    @staticmethod
    def change_password(user, password):
        user.set_password(password)
        user.save()
    
    @staticmethod
    def get_user_enc_key(user):
        aes = security.AES256(settings.SERVER_ENC_KEY)
        enc_key = aes.decrypt(user.enc_key)
        return enc_key

    @staticmethod
    def check_username_availability(username):
        return not User.objects.filter(username=username).exists()
    
    @staticmethod
    def change_names(user: User, first_name, last_name, username):
        if UserService.check_username_availability(username=username):
            user.username = username
        
        user.first_name = first_name.lower()
        user.last_name = last_name.lower()
        user.save()


class PreKeyBundleService:
    '''PreKeyBundle Service for pre-key bundle model crud operations'''
    @staticmethod
    def is_prekey_bundle_exists(user):
        return PreKeyBundle.objects.filter(user=user).exists()

    @staticmethod
    def __create_prekey_bundle(user, data):
        return PreKeyBundle.objects.create(
            user = user,
            reg_id = data.get('reg_id'),
            device_id = data.get('device_id'),
            prekeys = data.get('prekeys'),
            signed_prekey = data.get('signed_prekey'),
            identity_key = data.get('identity_key'),
        )
    
    @staticmethod
    def __get_prekey_bundle(user):
        if PreKeyBundleService.is_prekey_bundle_exists(user):
            return PreKeyBundle.objects.get(user=user)
        raise PreKeyBundleNotFoundError()
    
    @staticmethod
    def create_or_update_prekey_bundle(user, data):
        try:
            # fetching prekey_bundle
            prekey_bundle = PreKeyBundleService.__get_prekey_bundle(user)

            # updading prekey_bundle if already exists
            prekey_bundle.reg_id = data.get('reg_id')
            prekey_bundle.device_id = data.get('device_id')
            prekey_bundle.prekeys = data.get('prekeys')
            prekey_bundle.signed_prekey = data.get('signed_prekey')
            prekey_bundle.identity_key = data.get('identity_key')
            prekey_bundle.save()

            return prekey_bundle
        except:
            # creating new one
            PreKeyBundleService.__create_prekey_bundle(user, data) 
    
    @staticmethod
    def get_one_prekey_bundle(user):
        preKey_bundle_data = {}
        preKey_bundle = PreKeyBundleService.__get_prekey_bundle(user)
        preKeys = preKey_bundle.prekeys
        signed_prekey = preKey_bundle.signed_prekey
        prekey = preKeys.pop()

        preKey_bundle_data = {
            'reg_id': preKey_bundle.reg_id,
            'device_id': preKey_bundle.device_id,
            'prekeys': [
                    {
                    'id': prekey['id'],
                    'key': prekey['key'],
                }
            ],
            'signed_prekey': {
                'id': signed_prekey['id'],
                'key': signed_prekey['key'],
                'sign': signed_prekey['sign'],
            },
            'identity_key': preKey_bundle.identity_key,
        }

        prekeys_left = len(preKeys)
        preKey_bundle.prekeys = preKeys
        preKey_bundle.save()

        return preKey_bundle_data, prekeys_left
    
    @staticmethod
    def delete_prekey_bundle(user):
        if not PreKeyBundleService.is_prekey_bundle_exists(user):
            raise PreKeyBundleNotFoundError()
        
        PreKeyBundle.objects.get(user=user).delete()





class LoginStateTokenService:
    '''Login State Token Service for creating, fetching and deleting login token and it's state'''
    @staticmethod
    def create(user, user_agent_header, timeout):
        user_agent = user_agents.parse(user_agent_header)
        login_token = generator.generate_token()

        cache.set(f'{user.uid}:lst', {
            'login_token': login_token,
            'uid': user.uid,
            'device': user_agent.device.family,
            'os': user_agent.os.family,
            'browser': user_agent.browser.family
        }, timeout=timeout)

        return login_token
    
    @staticmethod
    def get(user):
        return cache.get(f'{user.uid}:lst')

    @staticmethod
    def delete(user):
        cache.delete(f'{user.uid}:lst')





class WebLoginStateTokenService:
    '''Web Login State Token Service for creating, fetching and deleting login token and it's state'''
    @staticmethod
    def create(user, user_agent_header, timeout):
        user_agent = user_agents.parse(user_agent_header)
        login_token = generator.generate_token()

        login_states = WebLoginState.objects.filter(user=user).order_by('-created_on')
        if len(login_states) == 5:
            login_states[0].delete()
        
        created_on = timezone.now()
        active_until = created_on + timedelta(seconds=timeout)
            
        login_state = WebLoginState.objects.create(
            user=user,
            token=login_token,
            device=user_agent.device.family,
            os=user_agent.os.family,
            browser=user_agent.browser.family,
            created_on=created_on,
            active_until=active_until,
        )

        return login_state
    
    @staticmethod
    def get(user, token):
        return WebLoginState.objects.get(user=user, token=token)

    @staticmethod
    def delete(user, token):
        WebLoginStateTokenService.get(user=user, token=token).delete()





class SignupService:
    '''Signup Service for signing up user'''
    @staticmethod
    def signup(data, platform=Platform.MOBILE):
        # retrieving data
        email = data.get('email')
        password = data.get('password')

        # generating otp, hashed otp and id
        actual_otp, hashed_otp = otp.generate()
        id = generator.generate_identity()

        # adding encrypted password an hasted otp to data dict
        aes = security.AES256(settings.SERVER_ENC_KEY)
        data['password'] = aes.encrypt(password)
        data['otp'] = hashed_otp

        # putting data into cache for validation
        cache.set(f'{id}:signup', data, timeout=settings.SIGNUP_EXPIRE_SECONDS)

        # generating signup otp token
        if platform == Platform.MOBILE:
            signup_otp_token = Jwt.generate(type='SO', data={'id': id}, seconds=settings.OTP_EXPIRE_SECONDS)
            signup_request_token = Jwt.generate(type='SR', data={'id': id}, seconds=settings.SIGNUP_EXPIRE_SECONDS)
        else:
            signup_otp_token = EncryptedJwt.generate(type='SO', data={'id': id}, seconds=settings.OTP_EXPIRE_SECONDS)
            signup_request_token = EncryptedJwt.generate(type='SR', data={'id': id}, seconds=settings.SIGNUP_EXPIRE_SECONDS)

        # sending otp mail to user
        Mailer.sendEmail(email, f'''Your Verification OTP is {actual_otp}. Please don't share this OTP to anyone else, valid for {settings.OTP_EXPIRE_SECONDS} seconds.''')

        return { 
            'message': f'Enter the otp sent to email {email}',
            'sot': signup_otp_token,
            'srt': signup_request_token
        }
    
    @staticmethod
    def verify_signup_verification_tokens(request, platform=Platform.MOBILE):
        # retriving headers data
        if platform == Platform.MOBILE:
            _sot = request.META.get('HTTP_SOT')
            _srt = request.META.get('HTTP_SRT')
            success_o, payload_o = Jwt.validate(_sot)
            success_r, payload_r = Jwt.validate(_srt)
        else:
            _sot = request.COOKIES.get('sot')
            _srt = request.COOKIES.get('srt')
            success_o, payload_o = EncryptedJwt.validate(_sot)
            success_r, payload_r = EncryptedJwt.validate(_srt)
            
        # validating token
        is_verified = success_o and payload_o.get('type') == 'SO' and success_r and payload_r.get('type') == 'SR' and payload_o['data']['id'] == payload_r['data']['id']
        id = payload_o['data']['id'] if is_verified else None
        return is_verified, id
    
    @staticmethod
    def retrieve_signup_cache_data(id):
        data = cache.get(f'{id}:signup')
        if not data:
            raise NoCacheDataError()
        return data
    
    @staticmethod
    def delete_signup_cache_data(id):
        cache.delete(f'{id}:signup')

    @staticmethod
    def create_user(data):
        # retriving hashed otp and decrypting password and changing the data dict password key value
        aes = security.AES256(settings.SERVER_ENC_KEY)
        data['password'] = aes.decrypt(data['password'])

        # creating user with user profile
        user = UserService.create_user(data)
        return user
    
    @staticmethod
    def verify_resent_otp_tokens(request, platform=Platform.MOBILE):
        # retriving headers data
        if platform == Platform.MOBILE:
            _srt = request.META.get('HTTP_SRT')
            success, payload = Jwt.validate(_srt)
        else:
            _srt = request.COOKIES.get('srt')
            success, payload = EncryptedJwt.validate(_srt)

        # validating token
        is_verified = success and payload.get('type') == 'SR'
        id = payload['data']['id'] if is_verified else None

        return is_verified, id
    
    @staticmethod
    def resent_otp(id, request, platform=Platform.MOBILE):
        # retriving data
        data = SignupService.retrieve_signup_cache_data(id)
        email = data.get('email')

        # generating new otp and changing otp value in data
        actual_otp, hashed_otp = otp.generate()
        data['otp'] = hashed_otp

        # putting data into cache for validation
        cache.set(f'{id}:signup', data, timeout=settings.SIGNUP_EXPIRE_SECONDS)

        # creating new signup otp token
        if platform == Platform.MOBILE:
            signup_otp_token = Jwt.generate(type='SO', data={'id': id}, seconds=settings.OTP_EXPIRE_SECONDS)
            signup_request_token = request.META.get('HTTP_SRT')
        else:
            signup_otp_token = EncryptedJwt.generate(type='SO', data={'id': id}, seconds=settings.OTP_EXPIRE_SECONDS)
            signup_request_token = request.COOKIES.get('srt')

        # sending otp email to user
        Mailer.sendEmail(email, f'''Your Verification OTP is {actual_otp}. Please don't share this OTP to anyone else, valid for {settings.OTP_EXPIRE_SECONDS} seconds.''')

        # sending response
        return { 
            'message': f'Enter the otp sent to email {email}',
            'sot': signup_otp_token,
            'srt': signup_request_token
        }




class LoginService:
    '''Login Service for login user'''

    @staticmethod
    def __login_authentication(data):
        return authenticate(email=data.get('email'), password=data.get('password'))
        

    @staticmethod
    def login(data):
        user = LoginService.__login_authentication(data)
        if user is not None:
            # updating messaging token
            UserService.update_fcm_token(user, data.get('msg_token'))
        
        return user
    
    @staticmethod
    def generate_auth_token(user: User, request, platform=Platform.MOBILE):
        if platform == Platform.MOBILE:
            # creating login state
            login_token = LoginStateTokenService.create(
                user=user,
                user_agent_header=request.META['HTTP_USER_AGENT'],
                timeout=settings.AUTH_EXPIRE_SECONDS
            )

            # creating logged in authenticatin token
            auth_token = Jwt.generate(type='LI', data={'uid': user.uid}, seconds=settings.AUTH_EXPIRE_SECONDS)
            ws_auth_token = Jwt.generate(type='WSLI', data={'uid': user.uid}, seconds=settings.AUTH_EXPIRE_SECONDS)

            # creating login check in cache to check whether the user is logged in or not
            cache.set(f'{user.uid}:login', {'uid': user.uid}, timeout=settings.AUTH_EXPIRE_SECONDS)

        else:
            # creating login state
            login_state = WebLoginStateTokenService.create(
                user=user,
                user_agent_header=request.META['HTTP_USER_AGENT'],
                timeout=settings.AUTH_EXPIRE_SECONDS
            )
            login_token = login_state.token

            # creating logged in authenticatin token
            auth_token = EncryptedJwt.generate(type='LI', data={'uid': user.uid}, seconds=settings.AUTH_EXPIRE_SECONDS)
            ws_auth_token = EncryptedJwt.generate(type='WSLI', data={'uid': user.uid}, seconds=settings.AUTH_EXPIRE_SECONDS)

        # creating logged in firebase auth token
        firebase_auth_token = create_custom_token(uid=user.uid)
        firebase_auth_token = firebase_auth_token.decode('utf-8')

        # getting user encryption key
        enc_key = UserService.get_user_enc_key(user)

        return { 
            'message': 'Account Logged in Successfully.',
            'at': auth_token,
            'lst': login_token,
            'wat': ws_auth_token,
            'fat': firebase_auth_token,
            'enc_key': enc_key,
            'settings': {
                'is_profile_private': user.is_private,
                'default_post_visibility': user.default_post_visibility,
                'default_reel_visibility': user.default_reel_visibility,
                'allow_chatgpt_info_access': user.allow_chatgpt_info_access,
            }
        }
    
    def retrieve_login_check_cache_data(user):
        return cache.get(f'{user.uid}:login', default=None)

    @staticmethod
    def logout(user, platform=Platform.MOBILE, web_platform_lst_token=None):
        if platform == Platform.MOBILE:
            # deleting login state
            LoginStateTokenService.delete(user=user)

            # deleting pre-keys
            PreKeyBundleService.delete_prekey_bundle(user)

            # deleting login check in cache to check whether the user is logged in or not
            cache.delete(f'{user.uid}:login')
        else:
            # deleting login state
            WebLoginStateTokenService.delete(user=user, token=web_platform_lst_token)
            
        # removing msg_token from user
        UserService.update_fcm_token(user=user)

        return { 
            'message': 'Account Logged out Successfully. See you soon.'
        }





class SignInWithGoogleService:
    '''Sigin in with google service'''
    
    class Action:
        def __init__(self, action =3, user=None, token=None):
            self.action = action
            self.user = user
            self.token = token

    @staticmethod
    def __verify_id_token(token):
        try:
            info = id_token.verify_oauth2_token(token, requests.Request())
            client_ids = [client_id.client_id for client_id in GoogleOAuthClientId.objects.all()]

            if info['aud'] not in client_ids:
                return None

            return info
        except:
            return None
    
    @staticmethod
    def verify_account_creation_token(request):
        _git = request.META.get('HTTP_GIT')
        _gsact = request.META.get('HTTP_GSACT')
    
        info = SignInWithGoogleService.__verify_id_token(_git)
        success, payload = Jwt.validate(_gsact)

        if not success or payload['type'] != 'GSAC' or payload['data']['email'] != info['email']:
            return None

        return info

    @staticmethod
    def signin(request) -> Action:
        '''
            function returns actions cases
            action 1: user authentication success and user exists
            action 2: user authentication success but doesn't exists
            action 3: user authentication failed
        '''
        _git = request.META.get('HTTP_GIT')
        info = SignInWithGoogleService.__verify_id_token(_git)
        email = info['email']
        
        if info is None:
            return SignInWithGoogleService.Action(action=3)
    
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            UserService.update_fcm_token(user=user, token=request.data.get('msg_token'))
            return SignInWithGoogleService.Action(action=1, user=user)
    
        else:
            account_creation_token = Jwt.generate(type='GSAC', data={'email': email}, seconds=settings.SIGNUP_EXPIRE_SECONDS)
            return SignInWithGoogleService.Action(action=2, token=account_creation_token)

    @staticmethod
    def create_user(data) -> User:
        if User.objects.filter(email=data['email']).exists():
            return User.objects.get(email=data['email'])
        else:
            return UserService.create_user(data)




class PasswordRecoveryService:
    '''Password Recovery Service used when user forgets account password'''
    @staticmethod
    def recover_password(user, data, platform=Platform.MOBILE):
        email = data.get('email')

        # generating otp and hashed otp
        actual_otp, hashed_otp = otp.generate()
        data['otp'] = hashed_otp

        # creating password recovery session
        cache.set(f'{user.uid}:pr', data, timeout=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS)

        # creating password recovery token
        if platform == Platform.MOBILE:
            password_recovery_otp_token = Jwt.generate(type='PRO', data={'uid': user.uid}, seconds=settings.OTP_EXPIRE_SECONDS)
            password_recovery_request_token = Jwt.generate(type='PRR', data={'uid': user.uid}, seconds=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS)
        else:
            password_recovery_otp_token = EncryptedJwt.generate(type='PRO', data={'uid': user.uid}, seconds=settings.OTP_EXPIRE_SECONDS)
            password_recovery_request_token = EncryptedJwt.generate(type='PRR', data={'uid': user.uid}, seconds=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS)

        # sending otp email
        Mailer.sendEmail(email, f'''Your Verification OTP is {actual_otp}. Please don't share this OTP to anyone else, valid for {settings.OTP_EXPIRE_SECONDS} seconds.''')

        return { 
            'message': f'Enter the otp sent to email {email}',
            'prot': password_recovery_otp_token,
            'prrt': password_recovery_request_token
        }
    
    @staticmethod
    def verify_recovery_verification_tokens(request, platform=Platform.MOBILE):
        # retriving headers data 
        if platform == Platform.MOBILE:
            _prot = request.META.get('HTTP_PROT')
            _prrt = request.META.get('HTTP_PRRT')
            success_o, payload_o = Jwt.validate(_prot)
            success_r, payload_r = Jwt.validate(_prrt)
        else:
            _prot = request.COOKIES.get('prot')
            _prrt = request.COOKIES.get('prrt')
            success_o, payload_o = EncryptedJwt.validate(_prot)
            success_r, payload_r = EncryptedJwt.validate(_prrt)
            
        # validating token
        is_verified = success_o and payload_o.get('type') == 'PRO' and success_r and payload_r.get('type') == 'PRR' and payload_o['data']['uid'] == payload_r['data']['uid']
        uid = payload_o['data']['uid'] if is_verified else None
        return is_verified, uid
    
    @staticmethod
    def retrieve_recovery_cache_data(uid):
        data = cache.get(f'{uid}:pr')
        if not data:
            raise NoCacheDataError()
        return data
    
    @staticmethod
    def delete_recovery_cache_data(uid):
        cache.delete(f'{uid}:pr')

    @staticmethod
    def generate_new_pass_token(uid, platform=Platform.MOBILE):
        # creating password recovery verification token
        if platform == Platform.MOBILE:
            password_recovery_new_pass_token = Jwt.generate(type='PRNP', data={'uid': uid}, seconds=settings.PASSWORD_EXPIRE_SECONDS)
        else:
            password_recovery_new_pass_token = EncryptedJwt.generate(type='PRNP', data={'uid': uid}, seconds=settings.PASSWORD_EXPIRE_SECONDS)

        # sending response
        return {
            'message': 'Create your new password.',
            'prnpt': password_recovery_new_pass_token
        }
    
    @staticmethod
    def verify_new_pass_tokens(request, platform=Platform.MOBILE):
        # retriving headers data
        if platform == Platform.MOBILE:
            _prnpt = request.META.get('HTTP_PRNPT')
            success, payload = Jwt.validate(_prnpt)
        else:
            _prnpt = request.COOKIES.get('prnpt')
            success, payload = EncryptedJwt.validate(_prnpt)
            
        # validating token
        is_verified = success and payload.get('type') == 'PRNP'
        uid = payload['data']['uid'] if is_verified else None
        return is_verified, uid
    
    @staticmethod
    def verify_resent_otp_tokens(request, platform=Platform.MOBILE):
        # retriving headers data
        if platform == Platform.MOBILE:
            _prrt = request.META.get('HTTP_PRRT')
            success, payload = Jwt.validate(_prrt)
        else:
            _prrt = request.COOKIES.get('prrt')
            success, payload = EncryptedJwt.validate(_prrt)

        # validating token
        is_verified = success and payload.get('type') == 'PRR'
        uid = payload['data']['uid'] if is_verified else None

        return is_verified, uid
    
    @staticmethod
    def resent_otp(uid, request, platform=Platform.MOBILE):
        # retriving email from payload and cache data
        data = PasswordRecoveryService.retrieve_recovery_cache_data(uid)

        # retriving data
        email = data.get('email')

        # generating otp and hashed otp
        actual_otp, hashed_otp = otp.generate()
        data['otp'] = hashed_otp

        # assiging new data to password recovery session
        cache.set(f'{uid}:pr', data, timeout=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS)

        # generating new password recovery token
        if platform == Platform.MOBILE:
            password_recovery_otp_token = Jwt.generate(type='PRO', data={'uid': uid}, seconds=settings.OTP_EXPIRE_SECONDS)
            password_recovery_request_token = request.META.get('HTTP_PRRT')
        else:
            password_recovery_otp_token = EncryptedJwt.generate(type='PRO', data={'uid': uid}, seconds=settings.OTP_EXPIRE_SECONDS)
            password_recovery_request_token = request.COOKIES.get('prrt')

        # sending otp email to user
        Mailer.sendEmail(email, f'''Your Verification OTP is {actual_otp}. Please don't share this OTP to anyone else, valid for {settings.OTP_EXPIRE_SECONDS} seconds.''')

        # sending response
        return { 
            'message': f'Enter the otp sent to email {email}',
            'prot': password_recovery_otp_token,
            'prrt': password_recovery_request_token
        }






class ProfileService:
    '''User Profile Service for crud operation to user profile section.'''

    @staticmethod
    def list_profile_photos(user):
        profile_photos = ProfilePhoto.objects.filter(user=user)
        photos = [{ 'id': model.id, 'photo': model.cdn_url } for model in profile_photos]
        return photos
    
    @staticmethod
    def list_profile_cover_photos(user):
        profile_cover_photos = ProfileCoverPhoto.objects.filter(user=user)
        cover_photos = [{'id': model.id, 'cover': model.cdn_url} for model in profile_cover_photos]
        return cover_photos
    
    @staticmethod
    def generate_user_profile(auth_user: User, uid):
        '''user - logged in user, uid - user uid who's profile is to be generated.'''

        user = UserService.get_user(uid)

        if BlockedUser.objects.filter(user=user, blocked_user=auth_user).exists():
            raise ProfileError('Profile not available as auth user is blocked.')

        # listing all photos
        photos = None
        cover_photos = None

        if auth_user.uid == user.uid or (auth_user.uid != user.uid and not user.is_private):
            photos = ProfileService.list_profile_photos(user)
            cover_photos = ProfileService.list_profile_cover_photos(user)

        # profile json response
        response = {
            'message': 'profile',
            'profile': {
                'uid': user.uid,
                'name': user.full_name,
                'username': user.username,
                'photo': user.photo_cdn_url,
                'cover_photo': user.cover_cdn_url,
                'gender': user.gender,
                'message': user.message,
                'bio': None,
                'interest': None,
                'website': None,
                'location': None,
                'post_count': user.post_count,
                'follower_count': user.follower_count,
                'following_count': user.following_count,
                'reel_count': user.reel_count,
                'settings': {
                    'is_profile_private': user.is_private,
                }
            },
            'profile_photos': photos,
            'profile_cover_photos': cover_photos
        }

        if auth_user.uid == user.uid or (auth_user.uid != user.uid and not user.is_private):
            response['profile']['bio'] = user.bio
            response['profile']['interest'] = user.interest
            response['profile']['website'] = user.website
            response['profile']['location'] = user.location

        # checking other user profile
        if auth_user.uid != user.uid:
            is_friend = False
            is_friend_requested = False
            friend_request_id = -1
            is_following = False
            is_follow_requested = False
            follow_request_id = -1
            is_blocked = False
                
            # finding out whether the user is friend or not
            if Friend.objects.filter(user=auth_user, friend=user).exists():
                is_friend = True
            else:
                try:
                    # finding out whether the user have send friend request of not
                    friend_request =  FriendRequest.objects.get(sender=user, receiver=auth_user)
                    is_friend_requested = True
                    friend_request_id = friend_request.id
                except:
                    pass
            
            # finding out whether the logged in user is a follower of the user
            if Following.objects.filter(user=auth_user, follow=user).exists():
                is_following = True

            try:
                # checking whether the user have sent a follow request to logged in user
                follow_request = FollowRequest.objects.get(sender=user, receiver=auth_user)
                is_follow_requested = True
                follow_request_id = follow_request.id
            except:
                pass
                
            # adding is blocked property if requested profile user is blocked by the logged in user
            if BlockedUser.objects.filter(user=auth_user, blocked_user=user).exists():
                is_blocked = True
                    
            # response fields from other users to logged in user
            response['is_friend'] = is_friend # denotes whether the requested user is friend of user or not
            response['is_friend_requested'] = is_friend_requested # denotes whether the requested user have send friend request to login user or not
            response['friend_request_id'] = friend_request_id # denotes friend request id
            response['is_following'] = is_following # denotes whether the logged in user follows the user or not
            response['is_follow_requested'] = is_follow_requested
            response['follow_request_id'] = follow_request_id
            response['is_blocked'] = is_blocked

        return response

    @staticmethod
    def update_profile(user: User, data):
        user.message = data.get('message')
        user.location = data.get('location').lower()
        user.interest = data.get('interest')
        user.bio = data.get('bio')
        user.website = data.get('website')

        # saving profile
        user.save()

        return {
            'message': 'Profile Updated.',
            'profile': {
                'name': user.full_name,
                'username': user.username,
                'photo': user.photo_cdn_url,
                'cover_photo': user.cover_cdn_url,
                'gender': user.gender,
                'message': user.message,
                'bio': user.bio,
                'interest': user.interest,
                'website': user.website,
                'location': user.location,
                'post_count': user.post_count,
                'follower_count': user.follower_count,
                'following_count': user.following_count,
                'reel_count': user.reel_count,
            }
        }
    
    @staticmethod
    def update_profile_photo(user: User, data):
        profile_photo = ProfilePhoto.objects.create(user=user, photo=data.get('photo'))
        user.photo = profile_photo.photo.name
        user.save()
        return {
            'message': 'Profile Photo Updated.',
            'photo': profile_photo.cdn_url,
            'id': profile_photo.id
        }
    
    @staticmethod
    def switch_profile_photo(user: User, profile_photo_id):
        if not ProfilePhoto.objects.filter(id=profile_photo_id, user=user).exists():
            raise NoDataError('Profile photo not found.')
        
        profile_photo = ProfilePhoto.objects.get(id=profile_photo_id, user=user)
        user.photo = profile_photo.photo.name
        user.save()
        
        # sending response
        return {
            'message': 'Photo updated.',
            'photo': profile_photo.cdn_url
        }
    
    @staticmethod
    def delete_profile_photo(user: User, profile_photo_id):
        if not ProfilePhoto.objects.filter(id=profile_photo_id, user=user).exists():
            raise NoDataError('Profile photo not found.')
        
        profile_photo = ProfilePhoto.objects.get(id=profile_photo_id, user=user)

        # removing profile photo if it seems to be deleted
        if user.photo == profile_photo.photo.name:
            user.photo = ''
            user.save()

        # deleting profile photo
        profile_photo.delete()

        # sending response
        return { 'message': 'Photo removed.' }
    
    @staticmethod
    def update_profile_cover(user: User, data):
        profile_cover_photo = ProfileCoverPhoto.objects.create(user=user, cover_photo=data.get('cover_photo'))
        user.cover_photo = profile_cover_photo.cover_photo.name
        user.save()
        return {
            'message': 'Profile Cover Photo Updated.',
            'cover': profile_cover_photo.cdn_url,
            'id': profile_cover_photo.id
        }
    
    @staticmethod
    def switch_profile_cover(user: User, profile_cover_id):
        if not ProfileCoverPhoto.objects.filter(id=profile_cover_id, user=user).exists():
            raise NoDataError('Profile cover photo not found.')
        
        cover_photo = ProfileCoverPhoto.objects.get(id=profile_cover_id, user=user)
        user.cover_photo = cover_photo.cover_photo.name
        user.save()
        
        # sending response
        return {
            'message': 'Cover photo updated.',
            'cover': cover_photo.cdn_url
        }
    
    @staticmethod
    def delete_profile_cover(user: User, profile_cover_id):
        if not ProfileCoverPhoto.objects.filter(id=profile_cover_id, user=user).exists():
            raise NoDataError('Profile cover photo not found.')
        
        cover_photo = ProfileCoverPhoto.objects.get(id=profile_cover_id, user=user)

        # removing profile photo if it seems to be deleted
        if user.cover_photo == cover_photo.cover_photo.name:
            user.cover_photo = ''
            user.save()

        # deleting profile photo
        cover_photo.delete()

        # sending response
        return { 'message': 'Cover photo removed.' }
