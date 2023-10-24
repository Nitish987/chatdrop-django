import notifier.services as notifier_services

from .models import Following, FollowRequest
from account.services import UserService
from .exceptions import FollowError
from django.core.paginator import Paginator
from privacy.models import BlockedUser




class FollowService:
    '''Follow service for sending and accepting follow request as well as unfollow.'''

    @staticmethod
    def is_following_exists(user, follow):
        return Following.objects.filter(user=user, follow=follow).exists()
    
    @staticmethod
    def get_following(user, follow):
       return  Following.objects.get(user=user, follow=follow)
    
    @staticmethod
    def __create_following(user, follow):
        return Following.objects.create(user=user, follow=follow)

    @staticmethod
    def is_follow_request_exists(sender, receiver):
        return FollowRequest.objects.filter(sender=sender, receiver=receiver).exists()
    
    @staticmethod
    def get_follow_request(sender, receiver):
        return FollowRequest.objects.get(sender=sender, receiver=receiver)
    
    @staticmethod
    def get_follow_request_by_id(receiver, id):
        return FollowRequest.objects.get(receiver=receiver, id=id)

    @staticmethod
    def __create_follow_request(sender, receiver):
        return FollowRequest.objects.create(
            sender=sender,
            receiver=receiver,
            message=f'{sender.username} wants to be follow you.'
        )
    
    @staticmethod
    def send_follow_request(auth_user, receiver_uid):
        receiver = UserService.get_user(receiver_uid)

        if receiver.uid == auth_user.uid:
            raise FollowError('Cannot follow yourself.')
    
        if not FollowService.is_follow_request_exists(sender=auth_user, receiver=receiver):
            FollowService.__create_follow_request(sender=auth_user, receiver=receiver)

            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=receiver,
                subject='Follow Request',
                body='want to be follow you.',
                type='FOLLOW_REQUEST'
            )
    
    @staticmethod
    def accept_follow_request(auth_user, request_id):
        follow_req = FollowService.get_follow_request_by_id(receiver=auth_user, id=request_id)

        if follow_req.sender.uid == auth_user.uid:
            raise FollowError('Cannot follow yourself.')
        
        profile = follow_req.sender

        if not FollowService.is_following_exists(user=follow_req.sender, follow=auth_user):
            FollowService.__create_following(user=follow_req.sender, follow=auth_user)

            # upgrading fan following
            auth_user.follower_count += 1
            auth_user.save()

            profile.following_count += 1
            profile.save()

            # deleting request
            follow_req.delete()

            # sending user a notification
            notifier_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=follow_req.sender,
                subject='Follow Request Accepted',
                body='accepted your follow request',
                type='FOLLOW_REQUEST'
            )
    
    @staticmethod
    def delete_follow_request(sender, receiver):
        if FollowService.is_follow_request_exists(sender=sender, receiver=receiver):
            FollowService.get_follow_request(sender=sender, receiver=receiver).delete()

    
    @staticmethod
    def unfollow(auth_user, following_uid):
        user = UserService.get_user(following_uid)

        if user.uid == auth_user.uid:
            raise FollowError('Cannot unfollow yourself.')
        
        if not FollowService.is_following_exists(user=auth_user, follow=user):
            raise FollowError('Have not followed this user.')

        following = FollowService.get_following(user=auth_user, follow=user)
        following.delete()

        # downgrading fan following
        user.follower_count -= 1
        user.save()

        auth_user.following_count -= 1
        auth_user.save()

    @staticmethod
    def force_unfollow(auth_user, follower_uid):
        user = UserService.get_user(follower_uid)

        if FollowService.is_following_exists(user=user, follow=auth_user):
            following = FollowService.get_following(user=user, follow=auth_user)
            following.delete()

            # downgrading fan following
            auth_user.follower_count -= 1
            auth_user.save()

            user.following_count -= 1
            user.save()
    
    @staticmethod
    def list_followers(auth_user, uid, page):
        user = UserService.get_user(uid)

        if user.is_private and auth_user.uid != user.uid:
            return []

        followers = Following.objects.filter(follow=user)

        pagination = Paginator(followers, 100)
        paginated_followers = pagination.get_page(int(page))

        follower_list = []
        for follower in paginated_followers.object_list:
            profile = UserService.get_user(uid=follower.user.uid)

            if not BlockedUser.objects.filter(user=profile ,blocked_user=auth_user).exists():

                follower_list.append({
                    'uid': profile.uid,
                    'name': profile.full_name,
                    'photo': profile.photo_cdn_url,
                    'username': profile.username,
                    'gender': profile.gender,
                    'message': profile.message,
                })
            
        return follower_list, paginated_followers.has_next()
    
    @staticmethod
    def list_followings(auth_user, uid, page):
        user = UserService.get_user(uid)

        if user.is_private and auth_user.uid != user.uid:
            return []

        followings = Following.objects.filter(user=user)

        pagination = Paginator(followings, 100)
        paginated_followings = pagination.get_page(int(page))

        following_list = []
        for following in paginated_followings.object_list:
            profile = UserService.get_user(uid=following.follow.uid)

            if not BlockedUser.objects.filter(user=profile ,blocked_user=auth_user).exists():

                following_list.append({
                    'uid': profile.uid,
                    'name': profile.full_name,
                    'photo': profile.photo_cdn_url,
                    'username': profile.username,
                    'gender': profile.gender,
                    'message': profile.message,
                })

        return following_list, paginated_followings.has_next()
        