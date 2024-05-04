from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import EloInfo, Rank, Match, Result
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
import random
from collections import deque  # Import deque

class MatchmakingConsumer(AsyncWebsocketConsumer):
    # Use deque for efficient pop and append operations
    waiting_users = deque()
    matchesmade = []
    ongoingmatches = []
    elo_range = 200

    # Updates the elo record for both players. Validates that they do not go exceed the specified minimums or maximums.
    @sync_to_async
    def update_elo_record(self, user, result):
        eloinfo_obj = EloInfo.objects.get(player=user)
        if result == True:
            if eloinfo_obj.elo > 1950:
                eloinfo_obj.elo = 2000
            else:
                eloinfo_obj.elo += 50
        else:
            if eloinfo_obj.elo < 50:
                eloinfo_obj.elo = 0
            else:
                eloinfo_obj.elo -= 50
        eloinfo_obj.save()
        return eloinfo_obj.elo

    @sync_to_async
    def create_match_record(self, match):
        # Extract user IDs from the match dictionary
        user_ids = [user.scope['user'].id for user in match.keys()]
        # Create a new Match object and save it to the database
        new_match = Match.objects.create()
        new_match.save()
        new_match.users.set(user_ids)
        new_match.save()
        return new_match

    # Creates the result record.
    @sync_to_async
    def create_result_record(self, match_obj, user_id, result):
        user_obj = User.objects.get(id=user_id)
        new_result = Result.objects.create(match_id=match_obj, user_id=user_obj, match_result=result)
        new_result.save()


    # Retrieve the username associated with the user's WebSocket connection
    @sync_to_async
    def get_username(self, user):
        user_id = user.scope['user'].id
        user_obj = User.objects.get(id=user_id)
        return user_obj.username

    # Retrieves the user's Elo rating
    @sync_to_async
    def get_eloinfo(self, user):
        user_id = user.scope['user'].id
        elo_obj = EloInfo.objects.get(player=user_id)
        return elo_obj.elo

    # Awaits the WebSocket connection being accepted
    async def connect(self):
        await self.accept()

    # Awaits the WebSocket being disconnected
    async def disconnect(self, close_code):
        if self in self.waiting_users:
            self.waiting_users.remove(self)
        pass

    # Awaits actions from the user's WebSocket connection.
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'queue_for_match':
            await self.queue_for_match()
        elif action == 'accept_match':
            await self.accept_match()
        elif action == 'deny_match':
            await self.deny_match()

    # Allows users to enter the queue for matchmaking
    async def queue_for_match(self):
        # print('A user has queued for a match')
        self.waiting_users.append(self)
        if len(self.waiting_users) >= 2:
            await self.match_users()
        pass

    async def notify_users_of_match(self, user1, user2, user1_elo, user2_elo):
        user1_username = await self.get_username(user1)
        user2_username = await self.get_username(user2)

        # Send notification to user1
        await user1.send(text_data=json.dumps({
            'message': 'You have been matched with another player!',
            'opponent_username': user2_username,
            'opponent_rating': user2_elo
        }))

        # Send notification to user2
        await user2.send(text_data=json.dumps({
            'message': 'You have been matched with another player!',
            'opponent_username': user1_username,
            'opponent_rating': user1_elo
        }))

    # Matches two users together using an algorithm, and sends messages to the users
    async def match_users(self):
        temporary_queue = deque()

        while self.waiting_users:
            user1 = self.waiting_users.popleft()
            user1_elo = await self.get_eloinfo(user1)

            match_found = False
            # Attempt to find a match in the remaining queue
            for i in range(len(self.waiting_users)):
                user2 = self.waiting_users[i]
                user2_elo = await self.get_eloinfo(user2)

                if abs(user1_elo - user2_elo) <= self.elo_range:
                    # If a match is found, notify users and create the match
                    await self.notify_users_of_match(user1, user2, user1_elo, user2_elo)
                    self.matchesmade.append({user1: 'pending', user2: 'pending'})
                    self.waiting_users.remove(user2)  # Remove the matched user from the queue
                    match_found = True
                    break

            if not match_found:
                # If no match found, move user1 to a temporary queue to retry after looping
                temporary_queue.append(user1)

        # Move unmatched users back to the main queue for the next round of matching
        self.waiting_users.extend(temporary_queue)


    # Allows users to accept a match and updates their status in the matchesmade list defined above.
    # Checks the match confirmation status after that.
    async def accept_match(self):
        for listindex, match in enumerate(self.matchesmade):
            if self in match.keys():
                print('User ID: \'', self.scope['user'].id, '\' has accepted.')
                self.matchesmade[listindex][self] = 'accepted'
                await self.send(text_data=json.dumps({'acceptdeny': 'accepted'}))
                await self.check_match_confirmation(listindex)
        pass

    # Allows users to deny a match and updates their status in the matchesmade list defined above.
    # Checks the match confirmation status after that.
    async def deny_match(self):
        for listindex, match in enumerate(self.matchesmade):
            if self in match.keys():
                print('User ID: \'', self.scope['user'].id, '\' has denied.')
                self.matchesmade[listindex][self] = 'denied'
                await self.send(text_data=json.dumps({'acceptdeny': 'denied'}))
                await self.check_match_confirmation(listindex)
        pass

    # Checks the match confirmation status
    async def check_match_confirmation(self, matchindex):
        # Ensures there are matchesmade to be found
        if len(self.matchesmade) < 1:
            pass
        else:
            # Checks if all the users accept, then passes to the next function
            if all(action == 'accepted' for action in self.matchesmade[matchindex].values()):
                await self.start_match(self.matchesmade[matchindex])
                try:
                    self.ongoingmatches.append(self.matchesmade[matchindex])
                    self.matchesmade.remove(matchindex)
                except:
                    pass
            # Checks if any of the users have declined, then passes to the next function.
            # Has a problem where it won't notify the other user about their acceptance status if the first user denies.
            # This is due to using the 'any' operator
            # Needs work
            elif any(action == 'denied' for action in self.matchesmade[matchindex].values()):
                await self.cancel_match(self.matchesmade[matchindex])
                try:
                    self.matchesmade.remove(matchindex)
                except:
                    pass

    # Begins the match. Needs work
    async def start_match(self, match):
        print('Both users have accepted the match. Starting match...')
        print(match.keys())
        users = list(match.keys())  # Convert dict_keys object to a list

        for user in users:
            await user.send(text_data=json.dumps({'startingcancelled': 'starting.'}))

        match_obj = await self.create_match_record(match)

        await self.get_results(match_obj, users)



    # Cancels the match and allows users to queue again.
    # Should send a message to the matchmaking.js file to allow for requeueing.
    # Should also remove messaging from the previously declined match.
    async def cancel_match(self, match):
        print('One or both users have denied the match. Cancelling match...')
        for i in match.keys():
            await i.send(text_data=json.dumps({'startingcancelled': 'cancelled.'}))

    async def get_results(self, match_obj, users):
        # Choose the random winner
        winner_index = random.randint(0, 1)
        loser_index = 1 - winner_index

        # Create result records for winner and loser
        await self.create_result_record(match_obj, users[winner_index].scope['user'].id, True)
        await self.create_result_record(match_obj, users[loser_index].scope['user'].id, False)

        # Notify users of their results
        await users[winner_index].send(text_data=json.dumps({'result': 'You won!'}))
        await users[loser_index].send(text_data=json.dumps({'result': 'You lost.'}))

        winnerrating = await self.update_elo_record(users[winner_index].scope['user'].id, True)
        loserrating = await self.update_elo_record(users[loser_index].scope['user'].id, False)

        await users[winner_index].send(text_data=json.dumps({'updated_rating': winnerrating}))
        await users[loser_index].send(text_data=json.dumps({'updated_rating': loserrating}))
