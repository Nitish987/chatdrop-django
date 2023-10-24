from django.urls import path
from . import web_views

urlpatterns = [
    path('v1/signup/', web_views.Signup.as_view(), name='web-signup'),
    path('v1/signup/verify/', web_views.SignupVerification.as_view(), name='web-signup-verification'),
    path('v1/signup/resent/otp/', web_views.ResentSignupOtp.as_view(), name='web-signup-resent-otp'),
    path('v1/login/', web_views.Login.as_view(), name='web-login'),
    path('v1/recovery/password/', web_views.PasswordRecovery.as_view(), name='web-account-recovery'),
    path('v1/recovery/password/verify/', web_views.PasswordRecoveryVerification.as_view(), name='web-account-recovery-verification'),
    path('v1/recovery/password/verify/new/', web_views.PasswordRecoveryNewPassword.as_view(), name='web-account-recovery-new-password'),
    path('v1/recovery/password/resent/otp/', web_views.ResentPasswordRecoveryOtp.as_view(), name='web-password-recovery-resent-otp'),
    path('v1/account/password/change/', web_views.ChangePassword.as_view(), name='web-password-change'),
    path('v1/account/names/change/', web_views.ChangeUserNames.as_view(), name='web-user-names-change'),
    path('v1/fcm/token/', web_views.UserFCMessagingToken.as_view(), name='web-fcm-token'),
    path('v1/login/check/', web_views.LoginCheck.as_view(), name='web-login-check'),
    path('v1/logout/', web_views.Logout.as_view(), name='web-logout'),
    path('v1/profile/<str:uid>/', web_views.UserProfile.as_view(), name='web-profile'),
    path('v1/profile/<str:uid>/photo/update/', web_views.ProfilePhotoUpdate.as_view(), name='web-profile-photo-update'),
    path('v1/profile/<str:uid>/cover/update/', web_views.ProfileCoverPhotoUpdate.as_view(), name='web-profile-cover-photo-update'),
    path('v1/profile/<str:uid>/photo/switch/<int:id>/', web_views.ProfilePhotoSwitch.as_view(), name='web-profile-showcase-photo'),
    path('v1/profile/<str:uid>/cover/switch/<int:id>/', web_views.ProfileCoverPhotoSwitch.as_view(), name='web-profile-showcase-cover'),
    path('v1/settings/', web_views.ProfileSettings.as_view(), name='web-profile-settings'),
]