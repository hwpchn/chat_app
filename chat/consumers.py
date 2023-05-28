from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
import json
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import asyncio


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        if await self.too_many_connections(self.scope['user']):
            raise DenyConnection("Too many connections.")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        self.timeout_task = asyncio.create_task(self.timeout())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        self.timeout_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message')
            token = text_data_json.get('token')
            if token:
                try:
                    Token(token)
                except (InvalidToken, TokenError) as e:
                    await self.close()
                else:
                    self.scope['user'] = await self.get_user_from_token(token)

            elif message:
                recipient = text_data_json['recipient']
                if await self.are_friends(self.scope['user'], recipient):
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message
                        }
                    )
        self.timeout_task.cancel()
        self.timeout_task = asyncio.create_task(self.timeout())

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    @database_sync_to_async
    def are_friends(self, user1_email, user2_email):
        User = get_user_model()
        user1 = User.objects.get(email=user1_email)
        user2 = User.objects.get(email=user2_email)
        return user1 in user2.friends.all() and user2 in user1.friends.all()

    @database_sync_to_async
    def get_user_from_token(self, token):
        User = get_user_model()
        return User.objects.get(token=token)

    @database_sync_to_async
    def too_many_connections(self, user):
        User = get_user_model()
        user = User.objects.get(username=user)
        return user.connections.count() >= 5

    async def timeout(self):
        await asyncio.sleep(300)
        await self.close()
