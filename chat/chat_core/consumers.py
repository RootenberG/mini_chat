import json
import logging

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Group, Message


class MessageConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = None
        self.room_name = None
        self.user_inbox = None

    async def process_pm(self, message):
        split = message.split(' ', 2)
        target = split[1]
        target_msg = split[2]

        # send private message to the target
        await self.channel_layer.group_send(
            f'inbox_{target}',
            {
                'type': 'private_message',
                'user': self.user.username,
                'message': target_msg,
            }
        )
        # send private message delivered to the user
        self.send(json.dumps({
            'type': 'private_message_delivered',
            'target': target,
            'message': target_msg,
        }))

    async def connect(self):
        logging.warning(self.scope)
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_name = 'chat_%s' % self.group_id

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        self.user_inbox = f'inbox_{self.user.username}'

        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(
                self.user_inbox,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if not self.user.is_authenticated:
            return
        data = json.loads(text_data)
        print(data)
        message = data['message']
        username = data['username']
        group_id = data['group_id']

        if message.startswith('/pm'):
            await self.process_pm(message)
            return

        await self.save_message(username, group_id, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receive message from group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))

    async def private_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def private_message_delivered(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, message, username, group_id):
        user = User.objects.get(username=username)
        group = Group.objects.get(slug=group_id)
        Message.objects.create(user=user, group=group, content=message.message)
