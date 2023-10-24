from channels.generic.websocket import AsyncJsonWebsocketConsumer
from utils.response import get_default_response_json
from utils.debug import debug_print
from channels.db import database_sync_to_async
from account.models import User
from friends.models import Friend

class SecretChatConsumer(AsyncJsonWebsocketConsumer):

    @database_sync_to_async
    def get_chat_room(self, sender):
        receiver = User.objects.get(uid=self.scope['url_route']['kwargs']['uid'])
        friend = Friend.objects.get(user=sender, friend=receiver)
        self.friends = [friend.user.uid, friend.friend.uid]
        return friend.chat_room
    

    async def connect(self):
        sender = self.scope['user']

        # checking user authentication
        if sender is None:
            await self.close()
        else:
            try:
                chat_room = await self.get_chat_room(sender)

                # creating communication channel
                self.group = f'{chat_room}_secret_chatroom'
                await self.channel_layer.group_add(self.group, self.channel_name)
                await self.accept()
            except:
                await self.close()
    
    async def receive_json(self, content, **kwargs):
        sender = self.scope['user']

        # checking user authentication
        if sender is None or content['sender_uid'] not in self.friends:
            await self.close()
        else:
            # sending chat message to user if user is authenticated
            await self.channel_layer.group_send(self.group, {
                'type': 'message.secret',
                'content': content
            })

    async def message_secret(self, event):
        res = get_default_response_json()
        res['success'] = True
        res['data'] = event['content']
        debug_print(res)
        await self.send_json(res)

    async def disconnect(self, code):
        try:
            # removing communication channel
            await self.channel_layer.group_discard(self.group, self.channel_name)
        except:
            pass