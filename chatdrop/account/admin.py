from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from . import models

# user admin portal
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'uid', 'is_active', 'is_admin', 'created_at', 'updated_at')
    list_filter = ('acc_type', 'is_active', 'is_signed', 'is_verified', 'is_admin',)
    fieldsets = (
        ('User', {'fields': ('first_name', 'last_name', 'email', 'country_code', 'phone', 'username', 'password')}),
        ('Profile', {'fields': ('gender', 'date_of_birth', 'photo', 'cover_photo', 'message', 'bio', 'interest', 'website', 'location', 'post_count', 'reel_count', 'follower_count', 'following_count', 'friend_count')}),
        ('Profile Settings', {'fields': ('is_private', 'default_post_visibility', 'default_reel_visibility', 'allow_chatgpt_info_access',)}),
        ('Account Type', {'fields': ('acc_type',)}),
        ('Account State', {'fields': ('is_signed', 'is_active', 'is_verified')}),
        ('Encryption Keys', {'fields': ('enc_key',)}),
        ('Tokens', {'fields': ('msg_token',)}),
        ('Permissions', {'fields': ('is_admin',)}),
        ('Terms and Conditions', {'fields': ('terms_conditions',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uid', 'email', 'first_name', 'last_name', 'username', 'password1', 'password2', 'acc_type', 'is_signed', 'is_active', 'is_admin', 'terms_conditions'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(models.User, UserAdmin)


# Profile photo admin portal
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo')

admin.site.register(models.ProfilePhoto, ProfilePhotoAdmin)


# Profile cover photo admin portal
class ProfileCoverPhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'cover_photo')

admin.site.register(models.ProfileCoverPhoto, ProfileCoverPhotoAdmin)


# Prekey bundle model admin panel
class PreKeyBundleAdmin(admin.ModelAdmin):
    list_display = ('user', 'reg_id')
    readonly_fields = ('reg_id', 'device_id', 'prekeys', 'signed_prekey', 'identity_key')

admin.site.register(models.PreKeyBundle, PreKeyBundleAdmin)


# Web Login state admin panel
class WebLoginStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'device', 'os', 'browser')
    readonly_fields = ('user', 'token', 'device', 'os', 'browser')

admin.site.register(models.WebLoginState, WebLoginStateAdmin)


# Google OAuth Client Id admin panel
class GoogleOAuthClientIdAdmin(admin.ModelAdmin):
    list_display = ('client_id',)

admin.site.register(models.GoogleOAuthClientId, GoogleOAuthClientIdAdmin)
