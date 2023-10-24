import json
import random
import post.services as post_services
import reel.services as reel_services
import privacy.services as privacy_services

from .models import Notification
from django.core.paginator import Paginator
from firebase_admin import messaging
from utils import time, debug
from deprecated.sphinx import deprecated


# Notification Pusher
class NotificationChannelService:
    @staticmethod
    def push_notification(from_user, to_user, subject, body, refer='', type='DEFAULT', extras={}):
        if type == 'SECRET_CHAT_MESSAGE':
            # notification content
            content = {
                'id': random.randint(0, 100),
                'from_user': {
                    'uid': from_user.uid,
                    'name': from_user.full_name,
                    'photo': from_user.photo_cdn_url,
                    'username': from_user.username,
                    'gender': from_user.gender,
                    'message': from_user.message,
                },
                'subject': from_user.full_name,
                'body': body,
                'type': type,
                'refer': refer,
                'refer_content': None,
                'is_read': False,
                'time': None
            }

            # sending notification throung FCM
            if to_user.msg_token != '' and to_user.msg_token != None:
                fcm_token = to_user.msg_token
                fcm = messaging.MulticastMessage(
                    [fcm_token],
                    data={
                        'content': json.dumps(content),
                        'extras': json.dumps(extras)
                    }
                )
                messaging.send_multicast(fcm)

        elif type == 'NORMAL_CHAT_MESSAGE':
            # notification content
            content = {
                'id': random.randint(0, 100),
                'from_user': {
                    'uid': from_user.uid,
                    'name': from_user.full_name,
                    'photo': from_user.photo_cdn_url,
                    'username': from_user.username,
                    'gender': from_user.gender,
                    'message': from_user.message,
                },
                'subject': subject,
                'body': body,
                'type': type,
                'refer': refer,
                'refer_content': None,
                'is_read': False,
                'time': None
            }

             # sending notification throung FCM
            if to_user.msg_token != '' and to_user.msg_token != None:
                fcm_token = to_user.msg_token
                fcm = messaging.MulticastMessage(
                    [fcm_token],
                    data={
                        'content': json.dumps(content),
                        'extras': json.dumps(extras)
                    },
                )
                messaging.send_multicast(fcm)

        else:
            # creating notification in database
            notification = Notification.objects.create(from_user=from_user, to_user=to_user, subject=subject, body=body, refer=refer, type=type)

            # calculating ago time
            time_ago = time.caltime_string(notification.created_at)

            # notification content
            content = {
                'id': notification.id,
                'from_user': {
                    'uid': from_user.uid,
                    'name': from_user.full_name,
                    'photo': from_user.photo_cdn_url,
                    'username': from_user.username,
                    'gender': from_user.gender,
                    'message': from_user.message,
                },
                'subject': notification.subject,
                'body': notification.body,
                'type': notification.type,
                'refer': notification.refer,
                'refer_content': None,
                'is_read': notification.read,
                'time': time_ago
            }

            try:
                # attaching post content in notification list if notification is related to post
                if notification.type == 'POST' or notification.type == 'POST_LIKE' or notification.type == 'POST_COMMENT' or notification.type == 'POST_COMMENT_LIKE':
                    if notification.refer is not None and notification.refer != '':
                        post = post_services.PostService.get_post(id=notification.refer)
                        content['refer_content'] = post_services.PostService.form_post_content_json_v2(post=post, auth_user=to_user)
                
                # attaching reel content in notification list if notification is related to reel
                elif notification.type == 'REEL' or notification.type == 'REEL_LIKE' or notification.type == 'REEL_COMMENT' or notification.type == 'REEL_COMMENT_LIKE':
                    if notification.refer is not None and notification.refer != '':
                        reel = reel_services.ReelService.get_reel(id=notification.refer)
                        content['refer_content'] = reel_services.ReelService.to_json(reel=reel, auth_user=to_user)
            except Exception as e:
                debug.debug_print(e)

            # sending notification throung FCM
            if to_user.msg_token != '' and to_user.msg_token != None:
                fcm_token = to_user.msg_token
                fcm = messaging.MulticastMessage(
                    [fcm_token],
                    notification=messaging.Notification(title=subject, body=f'{from_user.full_name} {notification.body}'),
                    data={
                        'content': json.dumps(content),
                        'extras': json.dumps(extras)
                    },
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            messaging.Aps(sound="default")
                        )   
                    ),
                    android=messaging.AndroidConfig(
                        notification=messaging.AndroidNotification(
                            sound="default",
                            priority="high"
                        )
                    )
                )
                messaging.send_multicast(fcm)




# Notification Paginator
class NotificationService:
    '''Notification Service for listing and reading notifications'''
    
    @staticmethod
    def read_notification(auth_user, notification_id):
        notification = Notification.objects.get(id=notification_id, to_user=auth_user)
        notification.read = True
        notification.save()

    @deprecated(version=1, reason='This method is deprecated, must use v2.')
    @staticmethod
    def list_notification(user, page):
        '''This method is deprecated, must use v2.'''
        # query notification and paginating
        notifications_objects = Notification.objects.filter(to_user=user).order_by('-id')
        pagination = Paginator(notifications_objects, 100)
        notifications = pagination.get_page(int(page))

        # paginating notification in json format
        notification_json = []
        for notification in notifications.object_list:
            # fetching profile of the user
            user = notification.from_user

            # calculating ago time
            time_ago = time.caltime_string(notification.created_at)

            notification_json.append({
                'id': notification.id,
                'from_user': {
                    'uid': user.uid,
                    'name': user.full_name,
                    'photo': user.photo_cdn_url,
                    'username': user.username,
                    'gender': user.gender,
                    'message': user.message,
                },
                'subject': notification.subject,
                'body': notification.body,
                'type': notification.type,
                'refer': notification.refer,
                'is_read': notification.read,
                'time': time_ago
            })
        
        return notification_json
    
    @staticmethod
    def list_notification_v2(auth_user, page):
        # query notification and paginating
        notifications_objects = Notification.objects.filter(to_user=auth_user).order_by('-id')
        pagination = Paginator(notifications_objects, 50)
        notifications = pagination.get_page(int(page))

        # paginating notification in json format
        notification_list = []
        for notification in notifications.object_list:
            if privacy_services.BlockedUserService.is_blocked(user=notification.from_user, blocked_user=auth_user):
                continue

            # fetching profile of the user
            user = notification.from_user

            # calculating ago time
            time_ago = time.caltime_string(notification.created_at)

            notification_json = {
                'id': notification.id,
                'from_user': {
                    'uid': user.uid,
                    'name': user.full_name,
                    'photo': user.photo_cdn_url,
                    'username': user.username,
                    'gender': user.gender,
                    'message': user.message,
                },
                'subject': notification.subject,
                'body': notification.body,
                'type': notification.type,
                'refer': notification.refer,
                'refer_content': None,
                'is_read': notification.read,
                'time': time_ago
            }

            try:
                # attaching post content in notification list if notification is related to post
                if notification.type == 'POST' or notification.type == 'POST_LIKE' or notification.type == 'POST_COMMENT' or notification.type == 'POST_COMMENT_LIKE':
                    if notification.refer is not None and notification.refer != '':
                        post = post_services.PostService.get_post(id=notification.refer)
                        notification_json['refer_content'] = post_services.PostService.form_post_content_json_v2(post=post, auth_user=auth_user)
                
                # attaching reel content in notification list if notification is related to reel
                elif notification.type == 'REEL' or notification.type == 'REEL_LIKE' or notification.type == 'REEL_COMMENT' or notification.type == 'REEL_COMMENT_LIKE':
                    if notification.refer is not None and notification.refer != '':
                        reel = reel_services.ReelService.get_reel(id=notification.refer)
                        notification_json['refer_content'] = reel_services.ReelService.to_json(reel=reel, auth_user=auth_user)
            except Exception as e:
                debug.debug_print(e)

            notification_list.append(notification_json)
        
        return notification_list, notifications.has_next()
