# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MatchmakingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Join a matchmaking channel
        await self.channel_layer.group_add("matchmaking", self.channel_name)

    async def disconnect(self, close_code):
        # Leave the matchmaking channel
        await self.channel_layer.group_discard("matchmaking", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        if action == 'join_queue':
            # Handle joining the queue
            await self.join_queue()
        elif action == 'accept_match':
            # Handle accepting a match
            await self.accept_match(data['match_id'])
        elif action == 'deny_match':
            # Handle denying a match
            await self.deny_match(data['match_id'])

    async def join_queue(self):
        # Logic to add player to the queue
        await self.channel_layer.group_send("matchmaking", {
            "type": "queue_update",
            "message": "Player joined the queue",
        })

    async def accept_match(self, match_id):
        # Logic to accept a match
        await self.channel_layer.group_send("matchmaking", {
            "type": "match_update",
            "message": "Match accepted",
        })

    async def deny_match(self, match_id):
        # Logic to deny a match
        await self.channel_layer.group_send("matchmaking", {
            "type": "match_update",
            "message": "Match denied",
        })

    async def queue_update(self, event):
        # Send queue update to all clients
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))

    async def match_update(self, event):
        # Send match update to all clients
        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
