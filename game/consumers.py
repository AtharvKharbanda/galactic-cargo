import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import GalacticDeck

game_state = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Initialize room if it doesn't exist
        if self.room_name not in game_state:
            game_state[self.room_name] = {
                'players': [],
                'deck': None,
                'center_card': None,
                'turn': 'player_1'
            }

        room = game_state[self.room_name]

        # Assign roles based on connection order
        if len(room['players']) == 0:
            self.role = 'player_1'
        elif len(room['players']) == 1:
            self.role = 'player_2'
        else:
            self.role = 'spectator' # Room is full!

        room['players'].append(self.role)

        # Tell the player who they are
        await self.send(text_data=json.dumps({
            'type': 'system_msg',
            'role': self.role,
            'message': f'Systems Online. You are assigned as {self.role.replace("_", " ").title()}.'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
        # CLEANUP: Remove the player from the room so the slot opens up again
        room = game_state.get(self.room_name)
        if room and self.role in room['players']:
            room['players'].remove(self.role)
            
            # Optional: If everyone leaves, delete the room entirely to save memory
            if len(room['players']) == 0:
                del game_state[self.room_name]

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        room = game_state.get(self.room_name)

        if action == 'start_game' and self.role == 'player_1':
            deck = GalacticDeck()
            room['deck'] = deck
            room['center_card'] = deck.draw(1)[0]
            room['turn'] = 'player_1'
            room['hand_counts'] = {'player_1': 7, 'player_2': 7} 
            
            # NEW: Draw hands for BOTH players
            hands = {
                'player_1': deck.draw(7),
                'player_2': deck.draw(7)
            }
            
            # Send the data to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_start_broadcast',
                    'top_card': room['center_card'],
                    'turn': room['turn'],
                    'hands': hands, # Pass the hands dictionary
                    'message': 'Incoming transmission: Game Started!'
                }
            )
            # Make sure you DELETE the extra `deal_hand` self.send block that used to be here!
            
        elif action == 'play_card':
            if room['turn'] != self.role:
                await self.send(text_data=json.dumps({'type': 'error', 'message': '⚠️ Not your turn.'}))
                return

            card = data.get('card')
            center = room['center_card']
            
            is_valid = (card['planet'] == center['planet'] or 
                        card['cargo'] == center['cargo'] or 
                        card['cargo'] == 'Wormhole')
            
            if is_valid:
                room['center_card'] = card
                room['hand_counts'][self.role] -= 1 
                
                # NEW FIX: Send a private message to the person who played it to update their screen
                await self.send(text_data=json.dumps({
                    'type': 'remove_card',
                    'card': card
                }))
                
                # WIN CONDITION CHECK
                if room['hand_counts'][self.role] == 0:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_over',
                            'winner': self.role,
                            'message': f"🏆 MISSION ACCOMPLISHED: {self.role.replace('_', ' ').title()} has emptied their cargo hold!"
                        }
                    )
                    return # Stop the game here!
                
                room['turn'] = 'player_2' if self.role == 'player_1' else 'player_1'
                
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'update_center',
                        'card': card,
                        'turn': room['turn'],
                        'message': f"{self.role.title()} logged new cargo: {card['cargo']} at {card['planet']}"
                    }
                )
            else:
                await self.send(text_data=json.dumps({'type': 'error', 'message': f"⚠️ Denied: Cannot dock {card['planet']} {card['cargo']}."}))

        # NEW ACTION: Drawing a card
        elif action == 'draw_card':
            if room['turn'] != self.role:
                return

            drawn = room['deck'].draw(1)
            if drawn:
                new_card = drawn[0]
                room['hand_counts'][self.role] += 1 # Add to official count
                
                # Send the card ONLY to the player who drew it
                await self.send(text_data=json.dumps({
                    'type': 'card_drawn',
                    'card': new_card,
                    'message': f"You drew {new_card['cargo']} from the deck."
                }))
                
                # Pass the turn to the opponent
                room['turn'] = 'player_2' if self.role == 'player_1' else 'player_1'
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'turn_switch',
                        'turn': room['turn'],
                        'message': f"{self.role.title()} drew a card. Turn passed."
                    }
                )
    
    async def card_drawn(self, event):
        await self.send(text_data=json.dumps(event))

    async def turn_switch(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_over(self, event):
        await self.send(text_data=json.dumps(event))

    async def game_start_broadcast(self, event):
        # NEW: Find this specific player's hand and send it to them
        my_hand = event['hands'].get(self.role, [])
        
        await self.send(text_data=json.dumps({
            'type': 'game_start_broadcast',
            'top_card': event['top_card'],
            'turn': event['turn'],
            'hand': my_hand,
            'message': event['message']
        }))

    async def update_center(self, event):
        await self.send(text_data=json.dumps(event))