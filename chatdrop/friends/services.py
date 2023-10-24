import notifier.services as notification_services

from .models import Friend, FriendRequest
from account.services import UserService
from .exceptions import FriendError
from utils import generator
from django.core.paginator import Paginator
from privacy.models import BlockedUser
from firebase_admin.firestore import firestore


# Friend Service
class FriendService:
    '''Friend Service which handle friend crud operations'''

    @staticmethod
    def is_friend_exists(user, friend):
        return Friend.objects.filter(user=user, friend=friend).exists()
    
    @staticmethod
    def get_friend(user, friend):
        return Friend.objects.get(user=user, friend=friend)
    
    @staticmethod
    def create_friend(user, friend):
        chat_room = generator.generate_string(prefix='chatroom', n=15)
        Friend.objects.create(user=user, friend=friend, chat_room=chat_room)
        Friend.objects.create(user=friend, friend=user, chat_room=chat_room)
        return chat_room
    
    @staticmethod
    def delete_friend(user, friend):
        if FriendService.is_friend_exists(user, friend):
            FriendService.get_friend(user, friend).delete()
            FriendService.get_friend(friend, user).delete()

            store = firestore.Client()
            store.collection('recents').document(user.uid).collection('chats').document(friend.uid).delete()
            store.collection('recents').document(friend.uid).collection('chats').document(user.uid).delete()


    @staticmethod
    def unfriend(auth_user, friend_uid):
        friend = UserService.get_user(friend_uid)

        if not FriendService.is_friend_exists(user=auth_user, friend=friend):
            raise FriendError('No Friendship found.')
        
        FriendService.delete_friend(user=auth_user, friend=friend)
        
        # decrementing friend count
        if auth_user.friend_count > 0:
            auth_user.friend_count -= 1
            auth_user.save()

        if friend.friend_count > 0:
            friend.friend_count -= 1
            friend.save()

    @staticmethod
    def has_friendship(auth_user, friend_uid):
        friend = UserService.get_user(friend_uid)
        return FriendService.is_friend_exists(user=auth_user, friend=friend)

    @staticmethod
    def list_all(auth_user, uid, page):
        user = UserService.get_user(uid)
        friends = Friend.objects.filter(user=user)

        pagination = Paginator(friends, 100)
        paginated_friends = pagination.get_page(int(page))

        friends_list = []
        for friend in paginated_friends.object_list:
            profile = friend.friend

            if not BlockedUser.objects.filter(user=profile ,blocked_user=auth_user).exists():

                user_json = {
                    'uid': profile.uid,
                    'name': profile.full_name,
                    'photo': profile.photo_cdn_url,
                    'username': profile.username,
                    'gender': profile.gender,
                    'message': profile.message,
                }

                if auth_user.uid == uid:
                    user_json['chatroom'] = friend.chat_room

                friends_list.append(user_json)
        
        return friends_list
    





# Friend Request Service
class FriendRequestService:
    '''Friend Request service for performing crud operations.'''
    @staticmethod
    def is_friend_request_exists(sender, receiver):
        return FriendRequest.objects.filter(sender=sender, receiver=receiver).exists()
    
    @staticmethod
    def get_friend_request(sender, receiver):
        return FriendRequest.objects.get(sender=sender, receiver=receiver)
    
    @staticmethod
    def get_friend_request_by_id(receiver, id):
        return FriendRequest.objects.get(receiver=receiver, id=id)
    
    @staticmethod
    def create_friend_request(sender, receiver):
        FriendRequest.objects.create(
            sender=sender,
            receiver=receiver,
            message=f'{sender.username} wants to be your Friend.'
        )

    @staticmethod
    def delete_friend_request(sender, receiver):
        if FriendRequestService.is_friend_request_exists(sender=sender, receiver=receiver):
            FriendRequestService.get_friend_request(sender=sender,receiver=receiver).delete()
    
    @staticmethod
    def send_friend_request(auth_user, receiver_uid):
        receiver = UserService.get_user(receiver_uid)

        if auth_user.uid == receiver_uid:
            raise FriendError('Cannot send same user friend request.')

        if FriendService.is_friend_exists(user=auth_user, friend=receiver):
            raise FriendError('Already Friends.')
        
        if not FriendRequestService.is_friend_request_exists(sender=auth_user, receiver=receiver):
            FriendRequestService.create_friend_request(sender=auth_user, receiver=receiver)

             # sending user a notification
            notification_services.NotificationChannelService.push_notification(
                from_user=auth_user,
                to_user=receiver,
                subject='Friend Request',
                body='want to be your friend.',
                type='FRIEND_REQUEST'
            )

    @staticmethod
    def accept_friend_request(auth_user, request_id):
        friend_req = FriendRequestService.get_friend_request_by_id(receiver=auth_user, id=request_id)

        if FriendService.is_friend_exists(user=auth_user, friend=friend_req.sender):
            raise FriendError('Already Friends.')

        # creating friendship
        FriendService.create_friend(user=auth_user, friend=friend_req.sender)

        # incrementing friend count
        if auth_user.friend_count == 0:
            auth_user.friend_count = Friend.objects.filter(user=auth_user).count()
        else:
            auth_user.friend_count += 1
        auth_user.save()

        if friend_req.sender.friend_count == 0:
            friend_req.sender.friend_count = Friend.objects.filter(user=friend_req.sender).count()
        else:
            friend_req.sender.friend_count += 1
        friend_req.sender.save()

        # deleting request
        friend_req.delete()

        # deleting alternate friend request
        FriendRequestService.delete_friend_request(sender=auth_user, receiver=friend_req.sender)

        # sending user a notification
        notification_services.NotificationChannelService.push_notification(
            from_user=friend_req.receiver,
            to_user=friend_req.sender,
            subject='Friend Request',
            body='accepted your friend request.',
            type='FRIEND_REQUEST'
        )

    @staticmethod
    def list_all(user, page):
        friend_requests = FriendRequest.objects.filter(receiver=user)

        pagination = Paginator(friend_requests, 100)
        paginated_friend_requests = pagination.get_page(int(page))

        friend_requests_list = []
        for request in paginated_friend_requests.object_list:
            profile = request.sender
            
            friend_requests_list.append({
                'uid': profile.uid,
                'name': profile.full_name,
                'photo': profile.photo_cdn_url,
                'username': profile.username,
                'gender': profile.gender,
                'message': profile.message,
            })
        
        return friend_requests_list