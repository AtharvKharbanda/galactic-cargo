import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import GalacticDeck

# A simple dictionary to remember the game state for each room
game_state = {}

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            'message': 'Systems Online. Connected to Galactic Command.'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'start_game':
            deck = GalacticDeck()
            starting_hand = deck.draw(7)
            top_card = deck.draw(1)[0]
            
            # SAVE THE STATE: Remember the deck and the center card for this room
            game_state[self.room_name] = {
                'deck': deck,
                'center_card': top_card
            }
            
            await self.send(text_data=json.dumps({
                'type': 'deal_hand',
                'hand': starting_hand,
                'top_card': top_card,
                'message': 'Incoming transmission: Cargo manifest received.'
            }))
            
        elif action == 'play_card':
            card = data.get('card')
            current_state = game_state.get(self.room_name)
            
            if current_state:
                center = current_state['center_card']
                
                # THE GALACTIC RULE: Must match Planet OR Cargo OR be a Wormhole
                is_valid = (
                    card['planet'] == center['planet'] or 
                    card['cargo'] == center['cargo'] or 
                    card['cargo'] == 'Wormhole'
                )
                
                if is_valid:
                    # Update the server's memory
                    current_state['center_card'] = card
                    
                    # Tell everyone the move was accepted
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'update_center',
                            'card': card,
                            'message': f"Ship logged new cargo: {card['cargo']} at {card['planet']}"
                        }
                    )
                else:
                    # REJECT THE MOVE: Tell just this player they messed up
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': f"⚠️ Transmission Denied: Cannot dock {card['planet']} {card['cargo']} at {center['planet']} {center['cargo']}."
                    }))

    async def update_center(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_center',
            'card': event['card'],
            'message': event['message']
        }))