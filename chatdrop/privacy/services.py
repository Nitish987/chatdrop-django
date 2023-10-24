from .models import BlockedUser, ReportedUser
from account.services import UserService
from friends.services import FriendService, FriendRequestService
from fanfollowing.services import FollowService


# Blocked User Paginator
class BlockedUserService:
    '''Blocked User Service for blocking and unblocking user.'''

    @staticmethod
    def is_blocked(user, blocked_user):
        return BlockedUser.objects.filter(user=user, blocked_user=blocked_user).exists()

    @staticmethod
    def block_user(auth_user, uid):
        user = UserService.get_user(uid)

        BlockedUser.objects.create(user=auth_user, blocked_user=user)

        if BlockedUserService.is_blocked(auth_user, user):

            # unfriend user if they are friends
            FriendService.delete_friend(user=auth_user, friend=user)

            # remove friend request if sent
            FriendRequestService.delete_friend_request(sender=auth_user, receiver=user)

            # remove alternate friend request if sent
            FriendRequestService.delete_friend_request(sender=user, receiver=auth_user)

            # unfollow user if they follows
            FollowService.force_unfollow(auth_user=auth_user, follower_uid=user.uid)

            # remove follow request if sent
            FollowService.delete_follow_request(sender=user, receiver=auth_user)
    
    @staticmethod
    def unblock(auth_user, uid):
        user = UserService.get_user(uid)

        if BlockedUserService.is_blocked(user=auth_user, blocked_user=user):
            BlockedUser.objects.get(user=auth_user, blocked_user=user).delete()

    @staticmethod
    def list_all(user):
        blocked_users = BlockedUser.objects.filter(user=user)

        blocked_users_list = []
        for blocked_user in blocked_users:
            profile = UserService.get_user(uid=blocked_user.blocked_user.uid)
            blocked_users_list.append({
                'uid': profile.uid,
                'name': profile.first_name,
                'photo': profile.photo_cdn_url,
                'username': profile.username,
                'gender': profile.gender,
                'message': profile.message,
            })
        
        return blocked_users_list





class ReportUserService:
    '''Report User Service for reporting user for unfair activities.'''

    @staticmethod
    def make_report(auth_user, uid, message):
        user = UserService.get_user(uid)

        ReportedUser.objects.create(user=auth_user, reported_user=user, message=message)