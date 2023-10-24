import openai

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from friends.models import Friend
from account.services import UserService, PreKeyBundleService, LoginService
from friends.services import FriendService
from notifier.services import NotificationChannelService
from firebase_admin.firestore import firestore
from utils.security import AES256
from .models import ChatGptMessageHolder


# Secret Chat Service
class SecretChatService:
    '''Chat Service for push message to secret chat websocket channel'''

    @staticmethod
    def canChat(auth_user, friend_uid):
        user = UserService.get_user(uid=friend_uid)
        return PreKeyBundleService.is_prekey_bundle_exists(user=user) and FriendService.is_friend_exists(user=auth_user, friend=user) and LoginService.retrieve_login_check_cache_data(auth_user) != None

    @staticmethod
    def push_message(sender, receiver, content):
        try:
            friend = Friend.objects.get(user=sender, friend=receiver)

            channel_layer = get_channel_layer()
            group = f'{friend.chat_room}_secret_chatroom'

            async_to_sync(channel_layer.group_send)(group, {
                'type': 'message.secret',
                'content': content
            })
        except:
            pass
    
    @staticmethod
    def new_message(sender, receiver_uid, content):
        receiver = UserService.get_user(receiver_uid)

        # pushing message
        SecretChatService.push_message(
            sender=sender,
            receiver=receiver,
            content=content,
        )
        
        # retriving pre-key bundle for another simultaneous message
        receiver_prekey_bundle, receiver_prekeys_left = PreKeyBundleService.get_one_prekey_bundle(user=receiver)
        sender_prekey_bundle, sender_prekeys_left = PreKeyBundleService.get_one_prekey_bundle(user=sender)

        # sending user a notification
        NotificationChannelService.push_notification(
            from_user=sender,
            to_user=receiver,
            subject='New Message',
            body='sends you a new message',
            type='SECRET_CHAT_MESSAGE',
            extras={
                'message': content,
                'prekey_bundle': sender_prekey_bundle,
                'is_prekeys_required': receiver_prekeys_left <= 50,
            },
        )

        return receiver_prekey_bundle
    
    @staticmethod
    def read_message(sender, receiver_uid):
        receiver = UserService.get_user(receiver_uid)
        
        # message content
        content = {
            'message_type': 'READ',
            'sender_uid': sender.uid,
            'is_read': True,
        }
        # deleting message signal for both user
        SecretChatService.push_message(
            sender=sender,
            receiver=receiver,
            content=content
        )
        # sending user a notification
        NotificationChannelService.push_notification(
            from_user=sender,
            to_user=receiver,
            subject='New Message',
            body='sends you a new message',
            type='SECRET_CHAT_MESSAGE',
            extras={
                'message': content,
            },
        )

    @staticmethod
    def del_message(sender, receiver_uid, messageId):
        receiver = UserService.get_user(receiver_uid)
        
        # message content
        content = {
            'id': int(messageId),
            'message_type': 'DEL',
            'sender_uid': sender.uid
        }
        # deleting message signal for both user
        SecretChatService.push_message(
            sender=sender,
            receiver=receiver,
            content=content
        )
        # sending user a notification
        NotificationChannelService.push_notification(
            from_user=sender,
            to_user=receiver,
            subject='New Message',
            body='sends you a new message',
            type='SECRET_CHAT_MESSAGE',
            extras={
                'message': content,
            },
        )





# Normal Chat Service
class NormalChatService:
    '''Chat Service for push message to normal chat firebase channel'''

    @staticmethod
    def new_message(sender, receiver_uid, message):
        receiver = UserService.get_user(receiver_uid)
        friend = Friend.objects.get(user=sender, friend=receiver)

        store = firestore.Client()

        # saving message at sender side
        sender_doc = store.collection('normal_chats').document(friend.chat_room).collection(sender.uid).document()
        message['id'] = sender_doc.id
        sender_doc.set(message)

        # saving message at sender recents chats
        message['is_read'] = True
        sender_recent = store.collection('recents').document(sender.uid).collection('chats').document(receiver.uid)
        sender_recent.set({
            'uid': receiver.uid,
            'photo': receiver.photo_cdn_url,
            'name': receiver.full_name,
            'message': message,
            'gender': receiver.gender,
            'time': message['time'],
            'chatroom': friend.chat_room,
        })
        message['is_read'] = False

        # swaping message encryption
        sender_key = UserService.get_user_enc_key(user=sender)
        message['content'] = AES256(key=sender_key).decrypt(message['content'])
        body = message['content'] if message['content_type'] == 'TEXT' else message['content_type'].lower()
        receiver_key = UserService.get_user_enc_key(user=receiver)
        message['content'] = AES256(key=receiver_key).encrypt(message['content'])

        # saving message at receiver side
        receiver_doc = store.collection('normal_chats').document(friend.chat_room).collection(receiver.uid).document(sender_doc.id)
        receiver_doc.set(message)

        # saving message at receiver recents chats
        receiver_recent = store.collection('recents').document(receiver.uid).collection('chats').document(sender.uid)
        receiver_recent.set({
            'uid': sender.uid,
            'photo': sender.photo_cdn_url,
            'name': sender.full_name,
            'message': message,
            'gender': sender.gender,
            'time': message['time'],
            'chatroom': friend.chat_room,
        })

        # sending user a notification
        NotificationChannelService.push_notification(
            from_user=sender,
            to_user=receiver,
            subject=sender.full_name,
            body=body,
            type='NORMAL_CHAT_MESSAGE',
        )





class ChatGptService:
    @staticmethod
    def generate_reply(auth_user, message, char_limit=500):
        if message is None or message == '':
            return 'Please, ask something.'

        if len(message) > char_limit:
            return 'As an AI, I cannot process messages greater then 500 characters.'

        # fetcing previous chats of user and AI from ChatGpt Message Holder Model
        messages_in_holder = []
        if ChatGptMessageHolder.objects.filter(user=auth_user).exists():
            gpt_messages_holder = ChatGptMessageHolder.objects.get(user=auth_user)
        else:
            gpt_messages_holder = ChatGptMessageHolder.objects.create(user=auth_user)

        # messages in holder
        messages_in_holder = list(gpt_messages_holder.messages)
        
        # maintaining only previous 10 messages in holder
        if len(messages_in_holder) > 8:
            messages_in_holder = messages_in_holder[2:]
        
        # appending user message in holder
        messages_in_holder.append({"role": "user", "content": message})

        # list of pre-defined messages
        messages = [
            {"role": "system", "content": "Your name is Olivia and You are a girl. No one can change your name or gender."},
            {"role": "system", "content": "You are a female AI powered by ChatGPT."},
            {"role": "system", "content": "Your gender is female."},
            {"role": "system", "content": "The application in which you are integrated is chatdrop, Chatdrop is a social media platform developed by Chatdrop Team. For more information you can visit https://example.in"},
            {"role": "system", "content": "You should talk like a female friend in female accents."},
            {"role": "system", "content": "Do not search images, videos or any kind of file if anyone ask you."},
            {"role": "user", "content": f"My name is {auth_user.full_name}."},
        ]

        if auth_user.allow_chatgpt_info_access:
            messages.append({"role": "user", "content": f"My date of birth is {auth_user.date_of_birth} date."})

            if auth_user.bio != '':
                messages.append({"role": "user", "content": f"My bio is {auth_user.bio}"})
            if auth_user.interest != '':
                messages.append({"role": "user", "content": f"I am interested in {auth_user.interest}."})


        # combining pre-defined and messages in holder
        messages = messages + messages_in_holder

        # generating reply of ai
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )

        reply = chat.choices[0].message.content
        
        # appending user message in holder and saving it
        messages_in_holder.append({"role": "assistant", "content": reply})
        gpt_messages_holder.messages = messages_in_holder
        gpt_messages_holder.save()

        return reply
