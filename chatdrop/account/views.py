from rest_framework.views import APIView
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from . import serializers
from .services import SignupService, LoginService, PreKeyBundleService, UserService, PasswordRecoveryService, ProfileService, SignInWithGoogleService
from .permissions import IsRequestValid, IsAccountCreationKeyValid
from .throttling import SignupThrottling, SignupVerificationThrottling, ResentSignupOtpThrottling, LoginThrottling, PasswordRecoveryThrottling, PasswordRecoveryVerificationThrottling, PasswordRecoveryNewPasswordThrottling, ResentPasswordRecoveryOtpThrottling, LogoutThrottling, AuthenticatedUserThrottling, ChangeNamesThrottling
from utils.response import Response
from utils.debug import debug_print



# Signup
class Signup(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [SignupThrottling]

    def post(self, request):
        try:
            serializer = serializers.SignupSerializer(data=request.data)

            if serializer.is_valid():
                response = SignupService.signup(serializer.data)
                
                # sending response
                return Response.success(response)

            # sending error response
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()





# Signup Verification
class SignupVerification(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAccountCreationKeyValid]
    throttle_classes = [SignupVerificationThrottling]

    def post(self, request):
        try:
            # validating token
            is_verified, id = SignupService.verify_signup_verification_tokens(request)

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

                    # prekeybundle serializer
                    prekey_serializer = serializers.UserPreKeyBundleSerializer(data=request.data.get('pre_key_bundle'))

                    # validating prekeybundle
                    if prekey_serializer.is_valid():

                        # saving prekeybundle
                        PreKeyBundleService.create_or_update_prekey_bundle(user, prekey_serializer.validated_data)

                        # generating auth tokens
                        response = LoginService.generate_auth_token(user, request)

                        # sending response
                        return Response.success(response)
                    
                    # sending error response
                    return Response.error('Account created but error occured while login. Please try login.')

                # sending error response
                return Response.errors(serializer.errors)
            
            return Response.error('Session out! Try again.')
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()





# Signup Resent OTP
class ResentSignupOtp(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [ResentSignupOtpThrottling]

    def post(self, request):
        try:
            is_verified, id = SignupService.verify_resent_otp_tokens(request)

            # validating token
            if is_verified:
                response = SignupService.resent_otp(id, request)

                # sending response
                return Response.success(response)
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()





# Login
class Login(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [LoginThrottling]

    def post(self, request):
        try:
            serializer = serializers.LoginSerializer(data=request.data)

            if serializer.is_valid():
                # authenticating user with valid credentials
                user = LoginService.login(serializer.data)

                if user is not None:
                    # prekeybundle serializer
                    prekey_serializer = serializers.UserPreKeyBundleSerializer(data=request.data.get('pre_key_bundle'))

                    # validating prekeybundle
                    if prekey_serializer.is_valid():

                        # saving prekeybundle
                        PreKeyBundleService.create_or_update_prekey_bundle(user, prekey_serializer.validated_data)

                        # generating auth tokens
                        response = LoginService.generate_auth_token(user, request)

                        # sending response
                        return Response.success(response)
                    
                    # sending error reponse
                    return Response.errors(prekey_serializer.errors)

                # sending invalid credentials error response
                return Response.error('Invalid Credentials.')

            # sending error reponse
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()




# Sign in with Google
class SigninWithGoogle(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [LoginThrottling]

    def post(self, request):
        try:
            prekey_serializer = serializers.UserPreKeyBundleSerializer(data=request.data.get('pre_key_bundle'))
            result = SignInWithGoogleService.signin(request)
            # validating prekeybundle
            if prekey_serializer.is_valid():
            
                if result.action == 1:
                    # saving prekeybundle
                    PreKeyBundleService.create_or_update_prekey_bundle(result.user, prekey_serializer.validated_data)

                    # generating auth tokens
                    response = LoginService.generate_auth_token(result.user, request)

                    # sending response
                    return Response.success(response)
                elif result.action == 2:
                    return Response.success({
                        'message': 'Google Sign in - Account Creation',
                        'gsact': result.token
                    })
            
            # sending error response
            return Response.errors(prekey_serializer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()



class GoogleSignInAccountCreation(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAccountCreationKeyValid]
    throttle_classes = [LoginThrottling]

    def post(self, request):
        try:
            info = SignInWithGoogleService.verify_account_creation_token(request)
            if info is None:
                return Response.error('Invalid Credentials')
            
            data = request.data
            data['first_name'] = info['given_name']
            data['last_name'] = info['family_name']
            data['email'] = info['email']

            serailizer = serializers.SignupSerializer(data=data)
            
            if serailizer.is_valid():
                user = SignInWithGoogleService.create_user(serailizer.validated_data)

                prekey_serializer = serializers.UserPreKeyBundleSerializer(data=request.data.get('pre_key_bundle'))

                # validating prekeybundle
                if prekey_serializer.is_valid():
                    # saving prekeybundle
                    PreKeyBundleService.create_or_update_prekey_bundle(user, prekey_serializer.validated_data)

                    # generating auth tokens
                    response = LoginService.generate_auth_token(user, request)

                    # sending response
                    return Response.success(response)
                
                # sending error reponse
                return Response.errors(prekey_serializer.errors)


            return Response.errors(serailizer.errors)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Password Recovery
class PasswordRecovery(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [PasswordRecoveryThrottling]

    def post(self, request):
        try:
            serializer = serializers.PasswordRecoverySerializer(data=request.data)

            if serializer.is_valid():
                response = PasswordRecoveryService.recover_password(serializer.user, serializer.data)

                # sending response
                return Response.success(response)

            # sending error response
            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()





# Password Recovery Verification
class PasswordRecoveryVerification(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [PasswordRecoveryVerificationThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_recovery_verification_tokens(request)

            # validating token
            if is_verified:
                data = PasswordRecoveryService.retrieve_recovery_cache_data(uid)

                # passing all the data to serializer from validations
                serializer = serializers.PasswordRecoveryVerificationSerializer(data=request.data, context={'hashed_otp': data.get('otp')})
                if serializer.is_valid():
                    # deleting cache and otp from data dict
                    PasswordRecoveryService.delete_recovery_cache_data(uid)
                    del data['otp']

                    response = PasswordRecoveryService.generate_new_pass_token(uid)

                    # sending response
                    return Response.success(response)

                # sending error response
                return Response.errors(serializer.errors)
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()





# Password Recovery New Password
class PasswordRecoveryNewPassword(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [PasswordRecoveryNewPasswordThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_new_pass_tokens(request)

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
                    return Response.success({ 
                        'message': 'Password changed successfully.'
                    })

                # sending error response
                return Response.errors(serializer.errors)
            
            return Response.error('Session out! Try again.') 
        except:
           return Response.something_went_wrong()





# Password Recovery Resent OTP
class ResentPasswordRecoveryOtp(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid]
    throttle_classes = [ResentPasswordRecoveryOtpThrottling]

    def post(self, request):
        try:
            is_verified, uid = PasswordRecoveryService.verify_resent_otp_tokens(request)

            # validating token
            if is_verified:
                response = PasswordRecoveryService.resent_otp(uid, request)

                # sending response
                return Response.success(response)
            
            return Response.error('Session out! Try again.')
        except:
            return Response.something_went_wrong()





# Change Password
class ChangePassword(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ChangeUserNames(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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





# User Prekey bundle
class UserPrekeyBundle(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def post(self, request):
        try:
            serializer = serializers.UserPreKeyBundleSerializer(data=request.data)

            # validating prekey bundle
            if serializer.is_valid():

                # saving prekey bundle
                PreKeyBundleService.create_or_update_prekey_bundle(request.user, serializer.validated_data)

                return Response.success({
                    'message': 'Bundle saved successfully.'
                })

            return Response.errors(serializer.errors)
        except:
            return Response.something_went_wrong()
    
    def get(self, request):
        try:
            user = UserService.get_user(request.query_params.get('of'))
            prekey_bundle, prekeys_left = PreKeyBundleService.get_one_prekey_bundle(user=user)
            
            return Response.success({
                'message': 'prekeybundle',
                'prekey_bundle': prekey_bundle,
            })
        except:
            return Response.something_went_wrong()





# User FCM Token
class UserFCMessagingToken(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class LoginCheck(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [AuthenticatedUserThrottling]

    def get(self, request):
        try:
            return Response.success({
                'message': 'Login Check'
            })
        except:
            return Response.something_went_wrong()





# Logout User
class Logout(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
    throttle_classes = [LogoutThrottling]

    def post(self, request):
        try:
            response = LoginService.logout(request.user)

            # sending response and logout current authenticated user
            return Response.success(response)
        except Exception as e:
            debug_print(e)
            return Response.something_went_wrong()




# Get User Profile
class UserProfile(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ProfilePhotoUpdate(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ProfileCoverPhotoUpdate(APIView):
    parser_classes = [FormParser, MultiPartParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ProfilePhotoSwitch(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ProfileCoverPhotoSwitch(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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
class ProfileSettings(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsRequestValid, IsAuthenticated]
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