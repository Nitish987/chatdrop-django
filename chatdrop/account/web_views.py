from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from .authentication import UserWebAuthentication
from . import serializers
from .services import SignupService, LoginService, UserService, PasswordRecoveryService, ProfileService, SignInWithGoogleService
from .throttling import SignupThrottling, SignupVerificationThrottling, ResentSignupOtpThrottling, LoginThrottling, PasswordRecoveryThrottling, PasswordRecoveryVerificationThrottling, PasswordRecoveryNewPasswordThrottling, ResentPasswordRecoveryOtpThrottling, LogoutThrottling, AuthenticatedUserThrottling, ChangeNamesThrottling
from utils.response import Response
from utils.debug import debug_print
from utils.platform import Platform
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.conf import settings


# Signup
@method_decorator(csrf_protect, name='dispatch')
class Signup(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [SignupThrottling]

    def post(self, request):
        try:
            serializer = serializers.SignupSerializer(data=request.data)
            if serializer.is_valid():
                content = SignupService.signup(serializer.validated_data, platform=Platform.WEB)

                message = content['message']
                signup_otp_token = content['sot']
                signup_request_token = content['srt']

                response = Response.success({'message': message})
                response.set_cookie(key='sot', value=str(signup_otp_token), max_age=settings.OTP_EXPIRE_SECONDS, httponly=True)
                response.set_cookie(key='srt', value=str(signup_request_token), max_age=settings.SIGNUP_EXPIRE_SECONDS, httponly=True)
                return response
            
            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Signup Verification
@method_decorator(csrf_protect, name='dispatch')
class SignupVerification(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [SignupVerificationThrottling]

    def post(self, request):
        try:
            # validating token
            is_verified, id = SignupService.verify_signup_verification_tokens(request, platform=Platform.WEB)

            if is_verified:
                # retriving email from payload and cache data
                data = SignupService.retrieve_signup_cache_data(id)

                # passing all the data for validation
                serializer = serializers.SignupVerificationSerializer(data=request.data, context={'hashed_otp': data['otp']})

                if serializer.is_valid():
                    # removing cache and deleting otp from data dict
                    SignupService.delete_signup_cache_data(id)
                    del data['otp']
                    
                    # creating user
                    user = SignupService.create_user(data)

                    # generating auth tokens
                    content = LoginService.generate_auth_token(user, request, plafrom=Platform.WEB)
                    message = content['message']
                    auth_token = content['at']
                    login_state_token = content['lst']
                    firebase_auth_token = content['fat']

                    response = Response.success({'message': message, 'fat': firebase_auth_token})
                    response.set_cookie(key='at', value=auth_token, max_age=settings.AUTH_EXPIRE_SECONDS, httponly=True)
                    response.set_cookie(key='lst', value=login_state_token, max_age=settings.AUTH_EXPIRE_SECONDS)

                    response.delete_cookie(key='sot')
                    response.delete_cookie(key='srt')
                    return response

                return Response.errors(serializer.errors)

            return Response.permission_denied()
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Signup Resent OTP
@method_decorator(csrf_protect, name='dispatch')
class ResentSignupOtp(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [ResentSignupOtpThrottling]

    def post(self, request):
        try:
            is_verified, id = SignupService.verify_resent_otp_tokens(request, platform=Platform.WEB)

            # validating token
            if is_verified:
                content = SignupService.resent_otp(id, request, platform=Platform.WEB)

                message = content['message']
                signup_otp_token = content['sot']
                signup_request_token = content['srt']

                # sending response
                response = Response.success({'message': message})
                response.set_cookie(key='sot', value=str(signup_otp_token), max_age=settings.OTP_EXPIRE_SECONDS, httponly=True)
                response.set_cookie(key='srt', value=str(signup_request_token), max_age=settings.SIGNUP_EXPIRE_SECONDS, httponly=True)
                return response
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()




# Login
@method_decorator(csrf_protect, name='dispatch')
class Login(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [LoginThrottling]

    def post(self, request):
        try:
            serializer = serializers.LoginSerializer(data=request.data)

            if serializer.is_valid():
                # authenticating user with valid credentials
                user = LoginService.login(serializer.data)

                if user is not None:
                    # generating auth tokens
                    content = LoginService.generate_auth_token(user, request, platform=Platform.WEB)
                    message = content['message']
                    auth_token = content['at']
                    login_state_token = content['lst']
                    firebase_auth_token = content['fat']

                    response = Response.success({'message': message, 'fat': firebase_auth_token})
                    response.set_cookie(key='at', value=auth_token, max_age=settings.AUTH_EXPIRE_SECONDS, httponly=True)
                    response.set_cookie(key='lst', value=login_state_token, max_age=settings.AUTH_EXPIRE_SECONDS)
                    return response

                # sending invalid credentials error response
                return Response.error('Invalid Credentials.')

            # sending error reponse
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()





# Password Recovery
@method_decorator(csrf_protect, name='dispatch')
class PasswordRecovery(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [PasswordRecoveryThrottling]

    def post(self, request):
        try:
            serializer = serializers.PasswordRecoverySerializer(data=request.data)

            if serializer.is_valid():
                content = PasswordRecoveryService.recover_password(serializer.user, serializer.data, platform=Platform.WEB)

                message = content['message']
                password_recovery_otp_token = content['prot']
                password_recovery_request_token = content['prrt']
                
                # sending response
                response = Response.success({ 'message': message})
                response.set_cookie(key='prot', value=password_recovery_otp_token, max_age=settings.OTP_EXPIRE_SECONDS, httponly=True)
                response.set_cookie(key='prrt', value=password_recovery_request_token, max_age=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS, httponly=True)
                return response

            # sending error response
            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Password Recovery Verification
@method_decorator(csrf_protect, name='dispatch')
class PasswordRecoveryVerification(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [PasswordRecoveryVerificationThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_recovery_verification_tokens(request, platform=Platform.WEB)

            # validating token
            if is_verified:
                data = PasswordRecoveryService.retrieve_recovery_cache_data(uid)

                # passing all the data to serializer from validations
                serializer = serializers.PasswordRecoveryVerificationSerializer(data=request.data, context={'hashed_otp': data.get('otp')})
                if serializer.is_valid():
                    # deleting cache and otp from data dict
                    PasswordRecoveryService.delete_recovery_cache_data(uid)
                    del data['otp']

                    content = PasswordRecoveryService.generate_new_pass_token(uid, platform=Platform.WEB)

                    message = content['message']
                    password_recovery_new_pass_token = content['prnpt']

                    # sending response
                    response = Response.success({ 'message': message })
                    response.set_cookie(key='prnpt', value=password_recovery_new_pass_token, max_age=settings.PASSWORD_EXPIRE_SECONDS, httponly=True)

                    response.delete_cookie(key='prot')
                    response.delete_cookie(key='prrt')
                    return response

                # sending error response
                return Response.errors(serializer.errors)
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()





# Password Recovery New Password
@method_decorator(csrf_protect, name='dispatch')
class PasswordRecoveryNewPassword(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [PasswordRecoveryNewPasswordThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_new_pass_tokens(request, platform=Platform.WEB)

            # validating token
            if is_verified:
                # fetching user
                user = UserService.get_user(uid)

                # passing all the data for validation
                serializer = serializers.PasswordRecoveryNewPassSerializer(data=request.data)

                if serializer.is_valid():   
                    # setting new password
                    UserService.change_password(user, serializer.validated_data.get('password'))

                    # sending response
                    response = Response.success({ 'message': 'Password changed successfully.' })
                    response.delete_cookie(key='prnpt')
                    return response

                # sending error response
                return Response.errors(serializer.errors)
            
            return Response.error('Session out! Try again.') 
        except:
           return Response.something_went_wrong()




# Password Recovery Resent OTP
@method_decorator(csrf_protect, name='dispatch')
class ResentPasswordRecoveryOtp(APIView):
    parser_classes = [JSONParser]
    throttle_classes = [ResentPasswordRecoveryOtpThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_resent_otp_tokens(request, platform=Platform.WEB)

            # validating token
            if is_verified:
                content = PasswordRecoveryService.resent_otp(uid, request, platform=Platform.WEB)

                message = content['message']
                password_recovery_otp_token = content['prot']
                password_recovery_request_token = content['prrt']
                
                # sending response
                response = Response.success({ 'message': message})
                response.set_cookie(key='prot', value=password_recovery_otp_token, max_age=settings.OTP_EXPIRE_SECONDS, httponly=True)
                response.set_cookie(key='prrt', value=password_recovery_request_token, max_age=settings.PASSWORD_RECOVERY_EXPIRE_SECONDS, httponly=True)
                return response
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()





# Change Password
@method_decorator(csrf_protect, name='dispatch')
class ChangePassword(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.ChangePasswordSerializer(data=request.data, context={'user': request.user})

            # validating current password
            if serializer.is_valid():

                # saving new password
                UserService.change_password(request.user, serializer.validated_data.get('new_password'))

                return Response.success({
                    'message': 'Password changed successfully.'
                })

            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()





# Change User Names
@method_decorator(csrf_protect, name='dispatch')
class ChangeUserNames(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChangeNamesThrottling]

    def post(self, request):
        try:
            serializer = serializers.ChangeUserNamesSerializer(data=request.data, context={'user': request.user})

            if serializer.is_valid():
                UserService.change_names(
                    user=request.user,
                    first_name=request.data.get('first_name'),
                    last_name=request.data.get('last_name'),
                    username=request.data.get('username'),
                )

                return Response.success({
                    'message': 'Names changed',
                })

            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# User FCM Token
@method_decorator(csrf_protect, name='dispatch')
class UserFCMessagingToken(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.UserFCMessagingTokenSerializer(data=request.data)

            # validating fcm token
            if serializer.is_valid():

                # updating fcm token
                UserService.update_fcm_token(user=request.user, token=serializer.validated_data.get('msg_token'))

                return Response.success({
                    'message': 'FCM Token updated.'
                })

            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()




# Login check
@method_decorator(csrf_protect, name='dispatch')
class LoginCheck(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            return Response.success({
                'message': 'Login Check'
            })
        except:
            return Response.something_went_wrong()





# Logout User
@method_decorator(csrf_protect, name='dispatch')
class Logout(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [LogoutThrottling]

    def post(self, request):
        try:
            content = LoginService.logout(
                user=request.user, 
                platform=Platform.WEB, 
                web_platform_lst_token=request.META.get('HTTP_LST'),
            )

            # sending response and logout current authenticated user
            response = Response.success(content)
            response.delete_cookie(key='at')
            response.delete_cookie(key='lst')
            return response
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Get User Profile
@method_decorator(csrf_protect, name='dispatch')
class UserProfile(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request, uid):
        try:
            response = ProfileService.generate_user_profile(request.user, uid)

            # sending profile in response
            return Response.success(response)
        except:
            return Response.something_went_wrong()
        
    def put(self, request, uid):
        try:
            if request.user.uid == uid:
                serializer = serializers.ProfileUpdateSerializer(data=request.data)

                if serializer.is_valid():
                    # updating profile
                    response = ProfileService.update_profile(request.user, serializer.validated_data)

                    # sending response
                    return Response.success(response)

                # sending error response
                return Response.errors(serializer.errors)
            
            # sending error response
            return Response.permission_denied()
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Change Profile Photo
@method_decorator(csrf_protect, name='dispatch')
class ProfilePhotoUpdate(APIView):
    parser_classes = [FormParser, MultiPartParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request, uid):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()

            serializer = serializers.ProfilePhotoUpdateSerializer(data=request.data)

            if serializer.is_valid():
                # updating profile photo
                response = ProfileService.update_profile_photo(request.user, serializer.validated_data)

                # sending response
                return Response.success(response)

            # sending error response
            return Response.errors(serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Change Profile Cover Photo
@method_decorator(csrf_protect, name='dispatch')
class ProfileCoverPhotoUpdate(APIView):
    parser_classes = [FormParser, MultiPartParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request, uid):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()
            
            serializer = serializers.ProfileCoverPhotoUpdateSerializer(data=request.data)

            if serializer.is_valid():
                # updating profile cover photo
                response = ProfileService.update_profile_cover(request.user, serializer.validated_data)

                # sending response
                return Response.success(response)

            # sending error response
            return Response.success(serializer.errors)
        except:
            return Response.something_went_wrong()





# User Profile photo switching
@method_decorator(csrf_protect, name='dispatch')
class ProfilePhotoSwitch(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def patch(self, request, uid, id):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()
            
            response = ProfileService.switch_profile_photo(request.user, id)
            
            # sending response
            return Response.success(response)
        except:
            return Response.something_went_wrong()

    def delete(self, request, uid, id):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()
            
            response = ProfileService.delete_profile_photo(request.user, id)

            # sending response
            return Response.success(response)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# User Profile Cover photo switching
@method_decorator(csrf_protect, name='dispatch')
class ProfileCoverPhotoSwitch(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def patch(self, request, uid, id):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()
            
            response = ProfileService.switch_profile_cover(request.user, id)

            # sending response
            return Response.success(response)
        except:
            return Response.something_went_wrong()

    def delete(self, request, uid, id):
        try:
            if request.user.uid != uid:
                return Response.permission_denied()
            
            response = ProfileService.delete_profile_cover(request.user, id)

            # sending response
            return Response.success(response)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Upadate Profile Settings
@method_decorator(csrf_protect, name='dispatch')
class ProfileSettings(APIView):
    parser_classes = [JSONParser]
    authentication_classes = [UserWebAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def put(self, request):
        try:
            try:
                key = request.data.get('key')
                value = request.data.get('value')       
            except:
                return Response.error('required key and value')

            # fetching profile
            user = request.user

            # updating profile with respect to given key
            if key == 'is_profile_private' and isinstance(value, bool):
                user.is_private = value
            elif key == 'default_post_visibility' and isinstance(value, str):
                user.default_post_visibility = value.upper()
            elif key == 'default_reel_visibility' and isinstance(value, str):
                user.default_reel_visibility = value.upper()
            elif key == 'allow_chatgpt_info_access' and isinstance(value, bool):
                user.allow_chatgpt_info_access = value
            
            # saving profile
            user.save()
            
            return Response.success({
                'message': 'profile settings updated',
            })
        except:
            return Response.something_went_wrong()