import logging
from django.test import TestCase
from channels.testing import WebsocketCommunicator
from ..consumers import MessageConsumer

class MessageTests(TestCase):
    async def test_my_consumer(self):
        communicator = WebsocketCommunicator(MessageConsumer.as_asgi())
        ...
