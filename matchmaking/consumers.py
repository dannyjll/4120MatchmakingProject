from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import EloInfo, Rank, Match, Result
from django.contrib.auth.models import User
from asgiref.sync import async_to_sync, sync_to_async


class MatchmakingConsumer(AsyncWebsocketConsumer):

    waiting_users = []
    matches = []

    @sync_to_async
    def get_username(self, user):
        # Retrieve the username associated with the user's WebSocket connection
        user_id = user.scope['user'].id
        user_obj = User.objects.get(id=user_id)
        return user_obj.username

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        if self in self.waiting_users:
            self.waiting_users.remove(self)
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'queue_for_match':
            await self.queue_for_match()
        elif action == 'accept_match':
            await self.accept_match()
        elif action == 'deny_match':
            await self.deny_match()

    async def queue_for_match(self):
        print('A user has queued for a match')
        self.waiting_users.append(self)
        if len(self.waiting_users) >= 2:
            await self.match_users()
        pass

    async def match_users(self):
        print('Matching users...')
        # Pop the first two users from the waiting list
        user1 = self.waiting_users.pop(0)
        user2 = self.waiting_users.pop(0)
        # Notify the users that they have been matched
        await user1.send(text_data=json.dumps({'message': 'You have been matched with another player!'}))
        await user2.send(text_data=json.dumps({'message': 'You have been matched with another player!'}))
        # You can send additional data like opponent username, etc.
        user1_username = await self.get_username(user1)
        user2_username = await self.get_username(user2)
        # For simplicity, let's assume their usernames are 'User1' and 'User2'
        await user1.send(text_data=json.dumps({'opponent_username': user2_username}))
        await user2.send(text_data=json.dumps({'opponent_username': user1_username}))
        match = ({user1: 'pending'}, {user2: 'pending'})
        self.matches.append(match)

    async def prompt_users_for_match(self):
        for user in self.waiting_users:
            await user.send(text_data=json.dumps({'message': 'Do you accept the match?'}))
            self.waiting_user_actions[user] = 'pending'

    async def accept_match(self):
        pass

    async def deny_match(self):
        pass

    async def check_match_confirmation(self):
        if len(self.waiting_user_actions) < 2:
            pass
        else:
            if all(action == 'accept' for action in self.waiting_user_actions.values()):
                await self.start_match()
            elif any(action == 'deny' for action in self.waiting_user_actions.values()):
                await self.cancel_match()

    async def start_match(self):
        print('Both users have accepted the match. Starting match...')

    async def cancel_match(self):
        print('One or both users have denied the match. Cancelling match...')

    async def match_update(self, event):
        pass
